import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.title("HTML constructor")

with open('page.html', 'r') as f:
    input_page = f.read()


def get_class_params(edited, page):
    html, css = find_html_and_css(page, edited)

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
    st.session_state.form_data = {
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
    html = raw_page[html_start - 1:html_end + 2]

    return html, css


def find_classes(page):
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


def add_text(page, text, color, noBg, bg, bold, italic, under, size, align):
    global classes
    if text == '':
        return
    class_counter = 0
    for i in range(len(classes) - 1, -1, -1):
        if classes[i].startswith("p"):
            class_counter = int(classes[i][1:]) + 1
            break
    css_string = f"\tcolor: {color};\n\ttext-align: {align};\n"
    if not noBg:
        css_string += f"""\tbackground: {bg};\n"""
    if text_size != 16:
        css_string += f"\tfont-size: {size}px;\n"
    page = page.replace("</style>", f".p{class_counter}" + "{\n" + css_string + "}\n</style>")

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
    page = page.replace("</body>", f"\t<div class=p{class_counter}>\n\t\t{string}\n\t</div>\n</body>")

    save(page)
    classes.append(f"p{class_counter}")
    return page


def edit_class(page, edited):
    html, css = find_html_and_css(page, edited)
    color = color_text
    text = text_to_add
    noBg = isNoBg
    bg = background
    bold = isBold
    italic = isItalic
    under = isUnder
    size = text_size
    align = alignment
    css_string = f"\tcolor: {color};\n\ttext-align: {align};\n"
    if not noBg:
        css_string += f"\tbackground: {bg};\n"
    if text_size != 16:
        css_string += f"""\tfont-size: {size}px;\n"""

    page = page.replace(css, f".{edited}" + "{\n\t" + css_string + "}\n")

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
    page = page.replace(html, f"\t<div class={edited}>\n\t\t{string}\n\t</div>\n")
    save(page)
    return page


def delete_class(page, html, css):
    page = page.replace(css, "")
    page = page.replace(html, "")
    save(page)
    return page


def save(page):
    with open('page.html', 'w') as f:
        f.write(page)


def clear_form():
    st.session_state.form_data = {
        'text': '',
        'color': '#ffffff',
        'noBg': True,
        'bgColor': '#ffffff',
        'isBold': False,
        'isItalic': False,
        'isUnder': False,
        'size': 16,
        'align': "left",
        'align-index': 0
    }


if 'form_data' not in st.session_state:
    clear_form()

if 'not_edit_mode' not in st.session_state or st.session_state.editing is None:
    st.session_state.not_edit_mode = True
if st.session_state.not_edit_mode:
    st.session_state.header = "Add text"
# editing form gui

with st.form("Edit/Add text", clear_on_submit=st.session_state.not_edit_mode):
    form_header = st.header(st.session_state.header)

    col1, col2, col3, col4, col5, col6 = st.columns([6, 2, 2, 1, 1, 2])
    text_to_add = col1.text_input("text to add", value=st.session_state.form_data['text'])
    color_text = col2.color_picker("color of text", value=st.session_state.form_data['color'])
    background = col3.color_picker("background color", value=st.session_state.form_data['bgColor'])
    isNoBg = col3.checkbox("no background", value=st.session_state.form_data['noBg'])
    isBold = col4.checkbox("Bold", value=st.session_state.form_data['isBold'])
    isItalic = col5.checkbox("Italic", value=st.session_state.form_data['isItalic'])
    isUnder = col6.checkbox("Underlined", value=st.session_state.form_data['isUnder'])

    col7, space, col8, col9 = st.columns([2, 1, 2, 12])
    text_size = col7.number_input("Enter text size", min_value=1, max_value=96,
                                  value=st.session_state.form_data['size'])
    alignment = col8.selectbox("Select text alignment", ["left", "center", "right"],
                               index=st.session_state.form_data['align-index'], key=st.session_state.form_data['align'])

    submit = st.form_submit_button("Submit")
    if submit:
        if st.session_state.not_edit_mode:
            input_page = add_text(input_page, text_to_add, color_text, isNoBg, background, isBold, isItalic, isUnder,
                                  text_size, alignment)
        else:
            input_page = edit_class(input_page, st.session_state.editing)

# main gui
st.header("Classes")
length = 0
num_of_columns = 15
with st.container():
    while length <= len(classes):
        if length + num_of_columns - len(classes) > 0:
            increment = length + num_of_columns - len(classes)
        else:
            increment = num_of_columns
        edit = st.columns(num_of_columns)
        sh_classes = classes[length:length + num_of_columns]
        length += num_of_columns
        for i, label in enumerate(sh_classes):
            if edit[i].button(label, key=label):
                st.session_state.button_pressed = label

if 'button_pressed' not in st.session_state:
    st.session_state.button_pressed = None
if 'editing' not in st.session_state:
    st.session_state.editing = None
if st.session_state.button_pressed:
    edited_class = st.session_state.button_pressed
    st.session_state.editing = edited_class
    st.session_state.button_pressed = None

if st.session_state.editing is None:
    st.header("Class isn't selected")
else:
    st.header("Selected class: " + st.session_state.editing)

with st.container():
    edit, delete, space = st.columns([1, 1, 10])
    if st.session_state.editing is None:
        edit = edit.button("Edit", disabled=True)
        delete = delete.button("Delete", disabled=True)
    else:
        edit = edit.button("Edit")
        delete = delete.button("Delete")
add = st.button("Add text")

if delete:
    if st.session_state.editing is not None:
        html, css = find_html_and_css(input_page, st.session_state.editing)
        input_page = delete_class(input_page, html, css)
        st.session_state.editing = None
        st.rerun()

if edit:
    if st.session_state.editing is not None:
        st.session_state.header = f"Edit {st.session_state.editing}"
        get_class_params(st.session_state.editing, input_page)
        st.session_state.not_edit_mode = False
        st.rerun()

if add:
    st.session_state.editing = None
    clear_form()
    st.rerun()

st.header("Page")
components.html(input_page, height=1000, scrolling=True)
