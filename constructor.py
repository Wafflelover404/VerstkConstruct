import streamlit as st
import streamlit.components.v1 as components

#set's the config of StApp
st.set_page_config(layout="wide")
margins_css = """
<style>
.main > div {
    padding-bottom: 0rem;
}
</style>
"""
st.markdown(margins_css, unsafe_allow_html=True)

#rewrite with creation of new page (for deploy)
with open('page.html', 'r') as f:
    input_page = f.read()

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

        if html.find("width") > 0:
            key = 'width'
            key_index = 2
        elif html.find('height') > 0:
            key = 'height'
            key_index = 1
        else:
            key = 'use native size'
            key_index = 0

        if key_index > 0:
            res = int(html[html.find('"')+1:html.find('>')-1])
        else:
            res = 400

        align = css[css.find("text-align"):]
        align = align[align.find(":") + 2: align.find(';')]
        align_index = 0
        if align == 'center':
            align_index = 1
        elif align == 'right':
            align_index = 2

        st.session_state.form_data[1] = {
            'url': url,
            'key': key,
            'key-index': key_index,
            'res': res,
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


classes = find_classes(input_page)

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
def create_image(url, key, res, align):

    string = f"<img src={url} "
    if key != "use native size":
        string += f'{key} = "{res}"'
    string += '>'
    css_string = f"\ttext-align: {align};\n"
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
        key = key_parameter
        res = resolution
        align = alignment
        new_class = 'i0'
        for i in range(len(classes) - 1, -1, -1):
            if classes[i].startswith("i"):
                new_class = 'i' + str(int(classes[i][1:]) + 1)
                break
        new_html, new_css = create_image(url, key, res, align)

    new_css = f".{new_class}" + "{\n" + new_css + "}\n</style>"
    new_html = f"\t<div class={new_class}>\n\t\t{new_html}\n\t</div>\n</body>"
    page = page.replace("</style>", new_css)
    page = page.replace("</body>", new_html)

    save(page)
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
        key = key_parameter
        res = resolution
        align = alignment
        new_html, new_css = create_image(url, key, res, align)

    new_css = f".{edited_class}" + "{\n\t" + new_css + "}\n"
    new_html = f"\t<div class={edited_class}>\n\t\t{new_html}\n\t</div>\n"

    page = page.replace(css, new_css)
    page = page.replace(html, new_html)

    save(page)
    return page

#deletes html of given class
def delete_class(page, html, css):
    page = page.replace(css, "")
    page = page.replace(html, "")
    save(page)
    return page

#saves page
def save(page):
    with open('page.html', 'w') as f:
        f.write(page)

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
        'key-index': 0,
        'key': "use native size",
        'res': 400,
        'align': "left",
        'align-index': 0
    }]


#init
if 'type' not in st.session_state:
    st.session_state.type = 'text'

if 'form_data' not in st.session_state:
    clear_form()

if 'not_edit_mode' not in st.session_state or st.session_state.editing_class is None:
    st.session_state.not_edit_mode = True
if st.session_state.not_edit_mode:
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
    col1, col2, space = st.columns([1, 1, 10])
    add_text = col1.button("Add text")
    add_image = col2.button("Add image")

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
            components.html(input_page, height=645, scrolling=True)

    #form with element's parameters
    with inspector:
        with st.container(height=685, border=True):
            with st.form("Inspector", clear_on_submit=st.session_state.not_edit_mode, border=False):
                st.subheader(st.session_state.header)
                if st.session_state.type == 'text':
                    text_to_add = st.text_input("text to add", value=st.session_state.form_data[0]['text'])
                    col1, col2 = st.columns(2)
                    color_text = col1.color_picker("color of text", value=st.session_state.form_data[0]['color'])
                    background = col2.color_picker("background color", value=st.session_state.form_data[0]['bgColor'])
                    isNoBg = col2.checkbox("no background", value=st.session_state.form_data[0]['noBg'])
                    isBold = st.checkbox("Bold", value=st.session_state.form_data[0]['isBold'])
                    isItalic = st.checkbox("Italic", value=st.session_state.form_data[0]['isItalic'])
                    isUnder = st.checkbox("Underlined", value=st.session_state.form_data[0]['isUnder'])
                    text_size = st.number_input("Enter text size", min_value=1, max_value=96, value=st.session_state.form_data[0]['size'])
                    alignment = st.selectbox("Select text alignment", ["left", "center", "right"], index=st.session_state.form_data[0]['align-index'], key=st.session_state.form_data[0]['align'])
                elif st.session_state.type == 'image':
                    image_url = st.text_input("url of image", value=st.session_state.form_data[1]['url'])

                    col1, col2 = st.columns(2)
                    key_parameter = col1.selectbox("Choose key parameter", ["use native size", "height", "width"], index=st.session_state.form_data[1]['key-index'], key=st.session_state.form_data[1]['key'])
                    resolution = col2.number_input("Enter key parameter size", min_value=1, max_value=4000, value=st.session_state.form_data[1]['res'])
                    alignment = st.selectbox("Select image alignment", ["left", "center", "right"], index=st.session_state.form_data[1]['align-index'], key=st.session_state.form_data[1]['align'])
                submit = st.form_submit_button("Submit")
                if submit:
                    if st.session_state.not_edit_mode:
                        input_page = add_class(input_page, st.session_state.type)
                        st.rerun()
                    else:
                        input_page = edit_class(input_page, st.session_state.type, st.session_state.editing_class)
                        st.rerun()

#button pressing checks
if delete:
    if st.session_state.editing_class is not None:
        html, css = find_html_and_css(input_page, st.session_state.editing_class)
        input_page = delete_class(input_page, html, css)
        st.session_state.editing_class = None
        st.session_state.not_edit_mode = True
        clear_form()
        st.rerun()

if edit:
    if st.session_state.editing_class is not None:
        st.session_state.header = f"Edit {st.session_state.editing_class}"
        if st.session_state.editing_class.startswith("p"):
            st.session_state.type = 'text'
        elif st.session_state.editing_class.startswith("i"):
            st.session_state.type = 'image'
        get_class_params(input_page, st.session_state.editing_class, st.session_state.type)
        st.session_state.not_edit_mode = False
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
