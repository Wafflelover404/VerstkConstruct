import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import requests
from io import BytesIO

#set's the config of StApp
st.set_page_config(layout="wide")
st.markdown("""
<style>
.main > div {
    padding-bottom: 0rem;
}
</style>
""", unsafe_allow_html=True)

#page initialization
if 'input_page' not in st.session_state:
    st.session_state.input_page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<style>
</style>
</head>
<body>
</body>
</html>"""

def get_image_dimensions(url):
    if url != '':
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        st.session_state.form_data[1]['orig-w'] = img.width
        st.session_state.form_data[1]['orig-h'] = img.height


#finds parameters of class for form filling in editing mode
def get_class_params(page, edited_class, type):
    html, css = find_html_and_css(page, edited_class)
    if type == 'text':
        color = css[css.find("color"):]
        color = color[color.find("#"):color.find("#") + 7]

        if css.find("background") > 0:
            noBg = False
            back = css[css.find("background"):]
            back = back[back.find("#"):back.find("#") + 7]
        else:
            noBg = True
            back = '#ffffff'

        if css.find("font-size") > 0:
            size = css[css.find("font-size"):]
            size = int(size[size.find(":") + 2: size.find('px')])
        else:
            size = 16

        align = css[css.find("text-align"):]
        align = align[align.find(":") + 2: align.find(';')]
        align_index = 0
        if align == 'center':
            align_index = 1
        elif align == 'right':
            align_index = 2

        inc = 3
        bold = False
        if html.find("<b>") + html.find("</b>") > 0:
            bold = True
            inc += 3
        italic = False
        if html.find("<i>") + html.find("</i>") > 0:
            italic = True
            inc += 3
        under = False
        if html.find("<u>") + html.find("</u>") > 0:
            under = True
            inc += 3

        text = html[html.find("<p>") + inc: html.find("</p>") - (inc + inc // 3 - 1) + 3]
        st.session_state.form_data[0] = {
            'text': text,
            'color': color,
            'noBg': noBg,
            'bgColor': back,
            'isBold': bold,
            'isItalic': italic,
            'isUnder': under,
            'size': size,
            'align': align,
            'align-index': align_index
        }
    elif type == 'image':
        html = html[html.find("src"):]
        url = html[html.find("src") + 4:html.find(" ")]

        get_image_dimensions(url)
        orig_w = st.session_state.form_data[1]['orig_w']
        orig_h = st.session_state.form_data[1]['orig_h']

        css2 = css
        keep = False
        native = False
        if css.find('px') > 0:
            res_w = int(css2[css2.find("width:")+6:css2.find("px")])
            css2 = css2[css2.find("px")+3:]
            print(css2)
            res_h = int(css2[css2.find("height:")+7:css2.find("px")])
            rt = "px"
            rt_index = 0
            res_wp = round(orig_w/res_w*100)
            res_hp = round(orig_h/res_h*100)
        elif css.find('%') > 0:
            res_wp = int(css2[css2.find("width:")+6:css2.find("%")])
            css2 = css2[css2.find("%"):]
            res_hp = int(css2[css2.find("height:")+7:css2.find("%")])
            rt = "%"
            rt_index = 1
            res_w = round(orig_w * res_wp / 100)
            res_h = round(orig_h * res_hp / 100)
        else:
            native = True
            res_w = orig_w
            res_h = orig_h
            res_wp = 100
            res_hp = 100
            rt = 'px'
            keep = True
            rt_index = 0

        align = css[css.find("text-align"):]
        align = align[align.find(":") + 2: align.find(';')]
        align_index = 0
        if align == 'center':
            align_index = 1
        elif align == 'right':
            align_index = 2

        st.session_state.form_data[1] = {
            'url': url,
            'native': native,
            'rt': rt,
            'rt-index': rt_index,
            'keep_props': keep,
            'orig_w': orig_w,
            'orig_h': orig_h,
            'res-w': res_w,
            'res-h': res_h,
            'res-wp': res_wp,
            'res-hp': res_hp,
            'align': align,
            'align-index': align_index
        }

#finds html and css of class to edit or delete it
def find_html_and_css(page, obj):
    class_css = page.find(f".{obj}")
    raw_page = page[class_css:]
    scope_index = raw_page.find("}") + class_css
    css = page[class_css:scope_index + 2]

    html_start = 0
    html_end = 0
    raw_page = page
    new_class = ""

    while new_class != obj:

        html_start = raw_page.find("<div")
        html_end = raw_page.find("</div>") + 5
        end = raw_page.find(">")
        new_class = raw_page[html_start:end]
        new_class = new_class[new_class.find("=") + 1:]
        new_class = new_class.replace(" ", "")
        if new_class == obj:
            break
        raw_page = raw_page[end + 1:]
        start = raw_page.find("class")
        end = raw_page.find(">")
        while end < start:
            raw_page = raw_page[end + 1:]
            start = raw_page.find("class")
            end = raw_page.find(">")
    html = raw_page[html_start-1:html_end+2]

    return html, css


def find_classes(page):  # rewrite
    body = page.find("<body>") + 6
    page = page[body:]
    found_classes = []
    # finding classes
    while page.find("class") > -1:

        start = page.find("class")
        end = page.find(">")
        new_class = page[start:end]
        new_class = new_class[new_class.find("=") + 1:]
        new_class = new_class.replace(" ", "")
        if new_class not in found_classes:
            found_classes.append(new_class)

        page = page[end + 1:]
        start = page.find("class")
        end = page.find(">")
        while end < start:
            page = page[end + 1:]
            start = page.find("class")
            end = page.find(">")

    return found_classes


classes = find_classes(st.session_state.input_page)

#creates text element with form parameters
def create_text(text, color, noBg, bg, bold, italic, under, size, align):
    css_string = f"\tcolor: {color};\n\ttext-align: {align};\n"
    if not noBg:
        css_string += f"""\tbackground: {bg};\n"""
    if text_size != 16:
        css_string += f"\tfont-size: {size}px;\n"

    string = f"<p>{text}</p>"
    if bold:
        string = string.replace("<p>", "<p><b>")
        string = string.replace("</p>", "</b></p>")
    if italic:
        string = string.replace("<p>", "<p><i>")
        string = string.replace("</p>", "</i></p>")
    if under:
        string = string.replace("<p>", "<p><u>")
        string = string.replace("</p>", "</u></p>")
    return string, css_string

#creates image element with form parameters
def create_image(new_class, url, rt, res_w, res_h, align):
    css_string = f"\ttext-align: {align};\n"
    string = f'<img src={url} class={new_class}>'
    if not isNative:
        css_string += f"\twidth: {res_w}{rt};\n\theight: {res_h}{rt};\n"
    return string, css_string

#adds new class with given type
def add_class(page, type):
    global classes

    new_class = 0
    if type == 'text':
        color = color_text
        text = text_to_add
        if text == '':
            return
        noBg = isNoBg
        bg = background
        bold = isBold
        italic = isItalic
        under = isUnder
        size = text_size
        align = alignment

        new_class = 'p0'
        for i in range(len(classes) - 1, -1, -1):
            if classes[i].startswith("p"):
                new_class = 'p' + str(int(classes[i][1:]) + 1)
                break

        new_html, new_css = create_text(text, color, noBg, bg, bold, italic, under, size, align)

    elif type == 'image':
        url = image_url
        if url == '':
            return
        rt = resolution_type
        if rt == 'px':
            res_w = st.session_state.form_data[1]['res-w']
            res_h = st.session_state.form_data[1]['res-h']
        else:
            res_w = st.session_state.form_data[1]['res-wp']
            res_h = st.session_state.form_data[1]['res-hp']
        align = alignment
        new_class = 'i0'
        for i in range(len(classes) - 1, -1, -1):
            if classes[i].startswith("i"):
                new_class = 'i' + str(int(classes[i][1:]) + 1)
                break
        new_html, new_css = create_image(new_class, url, rt, res_w, res_h, align)

    new_css = f".{new_class}" + "{\n" + new_css + "}\n</style>"
    new_html = f"\t<div class={new_class}>\n\t\t{new_html}\n\t</div>\n</body>"
    page = page.replace("</style>", new_css)
    page = page.replace("</body>", new_html)
    classes.append(new_class)
    return page

#edit class by replacing old html with new one
def edit_class(page, type, edited_class):
    html, css = find_html_and_css(page, edited_class)

    if type == 'text':
        color = color_text
        text = text_to_add
        if text == '':
            return
        noBg = isNoBg
        bg = background
        bold = isBold
        italic = isItalic
        under = isUnder
        size = text_size
        align = alignment

        new_html, new_css = create_text(text, color, noBg, bg, bold, italic, under, size, align)

    elif type == 'image':
        url = image_url
        if url == '':
            return
        rt = resolution_type
        if rt == 'px':
            res_w = st.session_state.form_data[1]['res-w']
            res_h = st.session_state.form_data[1]['res-h']
        else:
            res_w = st.session_state.form_data[1]['res-wp']
            res_h = st.session_state.form_data[1]['res-hp']
        align = alignment
        new_html, new_css = create_image(edited_class, url, rt, res_w, res_h, align)

    new_css = f".{edited_class}" + "{\n\t" + new_css + "}\n"
    new_html = f"\t<div class={edited_class}>\n\t\t{new_html}\n\t</div>\n"

    page = page.replace(css, new_css)
    page = page.replace(html, new_html)
    return page

#deletes html of given class
def delete_class(page, html, css):
    page = page.replace(css, "")
    page = page.replace(html, "")
    return page

#clears form on init or adding any element
def clear_form():
    st.session_state.form_data = [{
        'text': '',
        'color': '#ffffff',
        'noBg': True,
        'bgColor': '#ffffff',
        'isBold': False,
        'isItalic': False,
        'isUnder': False,
        'size': 16,
        'align': "left",
        'align-index': 0,
    }, {
        'url': '',
        'native': True,
        'rt': "px",
        'rt-index': 0,
        'keep_props': True,
        'orig_w': 1,
        'orig_h': 1,
        'res-w': 400,
        'res-h': 400,
        'res-wp': 100,
        'res-hp': 100,
        'align': "left",
        'align-index': 0,
    }]


#init
if 'type' not in st.session_state:
    st.session_state.type = 'text'

if 'form_data' not in st.session_state:
    clear_form()

if 'edit_mode' not in st.session_state or st.session_state.editing_class is None:
    st.session_state.edit_mode = False
if not st.session_state.edit_mode:
    if st.session_state.type == 'text':
        st.session_state.header = "Add text"
    if st.session_state.type == 'image':
        st.session_state.header = "Add image"

if 'button_pressed' not in st.session_state:
    st.session_state.button_pressed = None
if 'editing_class' not in st.session_state:
    st.session_state.editing_class = None



#interface
st.header("HTML constructor")

#adding buttons
with st.container(border=True):
    col1, col2, space, col3 = st.columns([1, 1.2, 14, 2])
    add_text = col1.button("Add text")
    add_image = col2.button("Add image")
    download = col3.download_button(label="Download HTML code", data=st.session_state.input_page, file_name="page.html", mime='text/html')

#main gui
with st.container():
    explorer, scene, inspector = st.columns([2, 6, 3], gap="medium")
    #a field with all classes in proj
    with explorer:
        with st.container(height=685, border=True):
            st.subheader("Explorer")
            with st.container(height=480, border=False):
                for i, label in enumerate(classes):
                    if st.button(label, key=label):
                        st.session_state.button_pressed = label

            if st.session_state.button_pressed:
                editing = st.session_state.button_pressed
                st.session_state.editing_class = editing
                st.session_state.button_pressed = None

            if st.session_state.editing_class is None:
                st.subheader("Class isn't selected")
            else:
                st.subheader("Selected class: " + st.session_state.editing_class)

            with st.container():
                edit, delete = st.columns(2)
                if st.session_state.editing_class is None:
                    edit = edit.button("Edit", disabled=True)
                    delete = delete.button("Delete", disabled=True)
                else:
                    edit = edit.button("Edit")
                    delete = delete.button("Delete")
    #page
    with scene:
        with st.container(height=685, border=True):
            components.html(st.session_state.input_page, height=645, scrolling=True)

    #form with element's parameters
    with inspector:
        with st.container(height=685, border=True):
            st.subheader(st.session_state.header)

            if st.session_state.type == 'text':
                image_url = '1'
                text_to_add = st.text_input("text to add", value=st.session_state.form_data[0]['text'])
                col1, col2 = st.columns(2)
                isNoBg = col2.checkbox("no background", value=st.session_state.form_data[0]['noBg'])
                col3, col4 = st.columns(2)
                color_text = col3.color_picker("color of text", value=st.session_state.form_data[0]['color'])
                background = col4.color_picker("background color", value=st.session_state.form_data[0]['bgColor'], disabled=isNoBg)
                isBold = st.checkbox("Bold", value=st.session_state.form_data[0]['isBold'])
                isItalic = st.checkbox("Italic", value=st.session_state.form_data[0]['isItalic'])
                isUnder = st.checkbox("Underlined", value=st.session_state.form_data[0]['isUnder'])
                text_size = st.number_input("Enter text size", min_value=1, max_value=96, value=st.session_state.form_data[0]['size'])
                alignment = st.selectbox("Select text alignment", ["left", "center", "right"], index=st.session_state.form_data[0]['align-index'], key=st.session_state.form_data[0]['align'])

            elif st.session_state.type == 'image':
                image_url = st.text_input("url of image", value=st.session_state.form_data[1]['url'])
                if image_url != '':
                    get_image_dimensions(image_url)
                    col1, col2 = st.columns(2)
                    isNative = col1.checkbox("native size", value=st.session_state.form_data[1]['native'])
                    if isNative:
                        st.session_state.form_data[1]['res-w'] = st.session_state.form_data[1]['orig-w']
                        st.session_state.form_data[1]['res-h'] = st.session_state.form_data[1]['orig-h']
                        st.session_state.form_data[1]['res-wp'] = 100
                        st.session_state.form_data[1]['res-hp'] = 100
                        st.session_state.form_data[1]['keep_props'] = True
                    resolution_type = col2.selectbox("set size type", ["px", "%"], index=st.session_state.form_data[1]['rt-index'], key=st.session_state.form_data[1]['rt'], disabled=isNative)
                    col3, col4, col5 = st.columns(3)

                    keepProps = col1.checkbox("keep proportions", value=st.session_state.form_data[1]['keep_props'], disabled=isNative)
                    if keepProps:
                        dimension = col4.selectbox("Select dimension to adjust", ["Width", "Height"])
                        if resolution_type == '%':
                            prop = st.session_state.form_data[1]['res-wp'] / st.session_state.form_data[1]['res-hp']
                            if dimension == "Width":
                                resolution_width = col5.number_input("width", min_value=1, max_value=200, value=st.session_state.form_data[1]['res-wp'], disabled=isNative)
                                st.session_state.form_data[1]['res-wp'] = resolution_width
                                st.session_state.form_data[1]['res-hp'] = round(st.session_state.form_data[1]['res-wp'] / prop)
                            else:
                                resolution_height = col5.number_input("height", min_value=1, max_value=200, value=st.session_state.form_data[1]['res-hp'], disabled=isNative)
                                st.session_state.form_data[1]['res-hp'] = resolution_height
                                st.session_state.form_data[1]['res-wp'] = round(st.session_state.form_data[1]['res-hp'] * prop)
                            st.session_state.form_data[1]['res-w'] = round(st.session_state.form_data[1]['orig-w'] * st.session_state.form_data[1]['res-wp'] / 100)
                            st.session_state.form_data[1]['res-h'] = round(st.session_state.form_data[1]['orig-h'] * st.session_state.form_data[1]['res-hp'] / 100)
                        else:
                            prop = st.session_state.form_data[1]['res-w'] / st.session_state.form_data[1]['res-h']
                            if dimension == "Width":
                                resolution_width = col5.number_input("width", min_value=1, max_value=5000, value=st.session_state.form_data[1]['res-w'], disabled=isNative)
                                st.session_state.form_data[1]['res-w'] = resolution_width
                                st.session_state.form_data[1]['res-h'] = round(st.session_state.form_data[1]['res-w'] / prop)
                            else:
                                resolution_height = col5.number_input("height", min_value=1, max_value=5000, value=st.session_state.form_data[1]['res-h'], disabled=isNative)
                                st.session_state.form_data[1]['res-h'] = resolution_height
                                st.session_state.form_data[1]['res-w'] = round(st.session_state.form_data[1]['res-h'] * prop)
                            st.session_state.form_data[1]['res-wp'] = round(st.session_state.form_data[1]['res-w'] / st.session_state.form_data[1]['orig-w'] * 100)
                            st.session_state.form_data[1]['res-hp'] = round(st.session_state.form_data[1]['res-h'] / st.session_state.form_data[1]['orig-h'] * 100)
                    else:
                        if resolution_type == '%':
                            resolution_width = col4.number_input("width", min_value=1, max_value=200, value=st.session_state.form_data[1]['res-wp'], disabled=isNative)
                            resolution_height = col5.number_input("height", min_value=1, max_value=200, value=st.session_state.form_data[1]['res-hp'], disabled=isNative)
                            st.session_state.form_data[1]['res-wp'] = resolution_width
                            st.session_state.form_data[1]['res-hp'] = resolution_height
                            st.session_state.form_data[1]['res-w'] = round(st.session_state.form_data[1]['orig-w'] * st.session_state.form_data[1]['res-wp']/100)
                            st.session_state.form_data[1]['res-h'] = round(st.session_state.form_data[1]['orig-h'] * st.session_state.form_data[1]['res-hp'] / 100)
                        else:
                            resolution_width = col4.number_input("width", min_value=1, max_value=5000, value=st.session_state.form_data[1]['res-w'], disabled=isNative)
                            st.session_state.form_data[1]['res-w'] = resolution_width
                            resolution_height = col5.number_input("height", min_value=1, max_value=5000, value=st.session_state.form_data[1]['res-h'], disabled=isNative)
                            st.session_state.form_data[1]['res-h'] = resolution_height
                            st.session_state.form_data[1]['res-wp'] = round(st.session_state.form_data[1]['res-w'] / st.session_state.form_data[1]['orig-w'] * 100)
                            st.session_state.form_data[1]['res-hp'] = round(st.session_state.form_data[1]['res-h'] / st.session_state.form_data[1]['orig-h'] * 100)

                    alignment = st.selectbox("Select image alignment", ["left", "center", "right"], index=st.session_state.form_data[1]['align-index'], key=st.session_state.form_data[1]['align'])
                else:
                    submit_fake = st.button("Submit image")
            submit = st.button("Submit", disabled=(image_url == ''))
            if submit:
                if not st.session_state.edit_mode:
                    st.session_state.input_page = add_class(st.session_state.input_page, st.session_state.type)
                    st.rerun()
                else:
                    st.session_state.input_page = edit_class(st.session_state.input_page, st.session_state.type, st.session_state.editing_class)
                    st.rerun()

#button pressing checks
if delete:
    if st.session_state.editing_class is not None:
        html, css = find_html_and_css(st.session_state.input_page, st.session_state.editing_class)
        st.session_state.input_page = delete_class(st.session_state.input_page, html, css)
        st.session_state.editing_class = None
        st.session_state.edit_mode = False
        clear_form()
        st.rerun()

if edit:
    if st.session_state.editing_class is not None:
        st.session_state.header = f"Edit {st.session_state.editing_class}"
        if st.session_state.editing_class.startswith("p"):
            st.session_state.type = 'text'
        elif st.session_state.editing_class.startswith("i"):
            st.session_state.type = 'image'
        get_class_params(st.session_state.input_page, st.session_state.editing_class, st.session_state.type)
        st.session_state.edit_mode = True
        st.rerun()

if add_text:
    st.session_state.type = 'text'
    st.session_state.editing_class = None
    clear_form()
    st.rerun()

if add_image:
    st.session_state.type = 'image'
    st.session_state.editing_class = None
    clear_form()
    st.rerun()
