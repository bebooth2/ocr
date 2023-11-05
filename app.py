from dash import Dash, dcc, html, Input, Output, State, ctx, callback 
from dash.exceptions import PreventUpdate
from dash_canvas import DashCanvas
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.express as px
from dash_bootstrap_templates import load_figure_template
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
from components import nav
from components import upload
from components.cv_variables import color_map_options
import pytesseract
from pytesseract import Output as output



app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.config.suppress_callback_exceptions = True
canvas_width = 600
canvas_height = 200

nav = nav.navbar
uploads = upload.upload
convert_contents_to_image = upload.convert_contents_to_image
parse_contents = upload.parse_contents
df = pd.DataFrame()

app.layout = html.Div(
    [
        dcc.Store(id="contents"),
        nav,
        # Canvas
        dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Optical Character Recognition", className="section_title"),
                html.P("Upload an image or use the signature pad to write your signature", className="section_title"),
            ],width=9),
            dbc.Col([
                html.H1(""),
                html.Br(),
                uploads(id="upload-image", style={"width": "100%", "height": "60px",'color':'azure','border':'azure',"border-width":"1px",'border-style':'dashed','text-align':'center'}, multiple=False),
               
            ],width=3),
        ], style={}),
        dbc.Row(
            [
                dbc.Col([
                    html.P(""),
                    html.P("Select different filters and Enhancements before processing to get better results", className="section_title"),

                    html.Div([
                        html.Label("Select Filter", id = "dropdown_label1",className="section_title"),
                        dcc.Dropdown(id="dropdown1", options=[{"label": "Filter 1", "value": "filter1"}]),
                        ], style={"margin-top": "5px", "margin-bottom": "5px"}),
                    html.Div([
                        html.Label("Select Enhancement", id = "dropdown_label2",className="section_title"),
                        dcc.Dropdown(id="dropdown2", options=[{"label": "Filter 2", "value": "filter2"}]),
                        ], style={"margin-top": "5px", "margin-bottom": "5px"}),
                    html.Div([
                        html.Label("Select Blurring", id = "dropdown_label3",className="section_title"),
                        dcc.Dropdown(id="dropdown3", 
                        options=[
                        {"label": "No Blur", "value": "no_blur"},
                        {"label": "Average Blur", "value": "blur"},  
                        {"label": "Gaussian Blur", "value": "gaussian_blur"},
                        {"label": "Median Blur", "value": "median_blur"},
                        {"label": "Bilateral Blur", "value": "bilateral_blur"}]),
                        ], 
                        id="dropdown_div3",
                        style={"margin-top": "5px", "margin-bottom": "5px","display":"none"}), 
                    html.Div([
                       dcc.Input(id="input1", type="number", placeholder="", value=75 , step= 5,debounce=True, style={'marginRight':'10px'}),
                        dcc.Input(id="input2", type="number", placeholder="",value= 90, step= 5, debounce=True),
                    ]), 
                    html.Div([
                        html.Label("Select Enhancement", id = "dropdown_label4",className="section_title"),
                        dcc.Dropdown(id="dropdown4", options=[{"label": "Filter 2", "value": "filter2"}]),
                        ], style={"margin-top": "5px", "margin-bottom": "5px","display":"none"}),
                           html.Div([
                        html.Label("Select Filter", id = "dropdown_label5",className="section_title"),
                        dcc.Dropdown(id="dropdown5", options=[{"label": "Filter 1", "value": "filter1"}]),
                        ], style={"margin-top": "5px", "margin-bottom": "5px","display":"none"}),
                    html.Div([
                        html.Label("Select Enhancement", id = "dropdown_label6",className="section_title"),
                        dcc.Dropdown(id="dropdown6", options=[{"label": "Filter 2", "value": "filter2"}]),
                        ], style={"margin-top": "5px", "margin-bottom": "5px","display":"none"}),
                ], width=5),
                dbc.Col([
                    html.Div([
                    html.P(
                            "Write inside the canvas with your stylus and press Sign",
                            className="section_title",
                        ),
                    html.Div(
                        DashCanvas(
                                id="canvas",
                                lineWidth=5,
                                # width= 550,
                                # height=canvas_height,
                                hide_buttons=[
                                    "zoom",
                                    "pan",
                                    "line",
                                    "pencil",
                                    "rectangle",
                                    "select",
                                ],
                               
                                lineColor="black",
                                goButtonTitle="Sign",
                            ),
                            className="canvas-outer",
                            style={"margin-top": "1em"},
                        ),
                    html.Div(
                        html.Button(id="clear", children="clear"),
                        className="v-card-content-markdown-outer",
                        ),
                        ], id="canvas-div", style={"margin-top": "1em", "display": "block"}),
                    html.Div(
                        [
                        html.Div(id="output-image-upload"),
                        html.Div([
                        html.Button(id="process", children="Process"),
                        html.Button(id="reset", children="Return Signature Pad"),
                        ], style={"margin-top": "1em", "display": "flex", "justify-content": "center"}),
                        ], id="output-image-upload_div", style={"margin-top": "1em","display":"none"},
                    ),
                    
        
               ],width=7),
            ]),
        dbc.Row([
                dbc.Col([
                   
                    html.Div(
                    [
                        html.B("Text Image to String", className="section_title"),
                        dcc.Loading(dcc.Markdown(id="text-output", children="")),
                    ],
                    className="v-card-content",
                    style={"margin-top": "1em",'color':'red'},
                ),
            ], width={'size':4}),
            dbc.Col([
                   
                    html.Div(
                    [
                        html.B("Text Image To Data", className="section_title"),
                        dcc.Loading(dcc.Markdown(id="text-output2", children="")),
                    ],
                    className="v-card-content",
                    style={"margin-top": "1em",'color':'red'},
                ),
            ], width={'size':4}),
        
        
        
        
        ],),
    ], className="page-container", style={"max-width": "100%"}),
    ])
 
@app.callback([Output('contents','data'),
               Output("output-image-upload", "children"),    
              Output("output-image-upload_div", "style"),
              Output("upload-image", "last_modified"),
              Output("canvas-div", "style"),
              Output("dropdown1", "options"),
              Output("dropdown_label1", "children"),
              Output("dropdown2", "options"),
              Output("dropdown_label2", "children"),
              Output("dropdown_div3", "style"),],
              [Input("reset", "n_clicks"),
              Input('dropdown1', 'value'),
              Input('dropdown2', 'value'),
              Input('dropdown3', 'value'),
              Input('input1', 'value'),
              Input('input2', 'value'),
              Input("upload-image", "contents"),
              State("upload-image", "filename"),
              State("upload-image", "last_modified"),
               ])
def update_output(n_click, color_value,gray_scale, blur,input1, input2, list_of_contents, list_of_names, list_of_dates):
    print(ctx.triggered[0]["prop_id"])
    button_clicked = ctx.triggered_id
    print(button_clicked)
    if button_clicked == "reset" :
        return None, {"display":"none"}, None ,{"display":"block"}, [{"label": "Filter 1", "value": "filter1"}],"Select Filter" ,[{"label": "Filter 2", "value": "filter2"}] ,"Select Enhancement" 
    elif list_of_dates is not None or button_clicked == "dropdown1" or button_clicked == "dropdown2" or button_clicked == "dropdown3" or button_clicked == "input1" or button_clicked == "input2": 
        children, contents = parse_contents(list_of_contents, list_of_names, list_of_dates, color_value, gray_scale, blur, input1, input2)
        return (contents , children, {"display":"block"},
                None, {"display":"none"},color_map_options,
                 "Select Colormap", [{"label":"No Gray Scale", "value":"no_gray"},
                 {"label":"No Gray Scale and Dilate", "value":"no_gray_dilate"}, 
                 {"label": "Gray_scale", "value": "gray"}, 
                 {"label":"Gray_scale_dilate","value":"gray_dilate"},
                 {"label":"Gray_scale_erode","value":"gray_erode"},
                 {"label":"Gray_scale_dilate_erode","value":"gray_dilate_erode"},
                 {"label":"Gray_scale_erode_dilate","value":"gray_erode_dilate"},
                 {"label":"Gray_scale_adaptive","value":"gray_adaptive"}], 
                 "Select Enhancement",{"display":'block'})
    raise PreventUpdate

# @app.callback(Output("canvas", "json_objects"), [Input("clear", "n_clicks")])
# def clear_canvas(n):
#     if n is None:
#         raise PreventUpdate
#     strings = ['{"objects":[ ]}', '{"objects":[]}']
#     return strings[n % 2]


@app.callback(
    Output("text-output", "children"), 
    Output("text-output2", "children"),
    [Input("process", "n_clicks"),
    State("contents", "data")],
)
def update_data(nclicks, contents):
    if contents:
    
        # try:
        #     mask = parse_jsonstring(string, shape=(canvas_height, canvas_width))
        # except:
        #     return "Out of Bounding Box, click clear button and try again"
        # np.savetxt('data.csv', mask) use this to save the canvas annotations as a numpy array
        # Invert True and False
        # mask = (~mask.astype(bool)).astype(int)
        img = convert_contents_to_image(contents)
       
        

        # this is from canvas.utils.image_string_to_PILImage(image_string)
        # img = Image.open(BytesIO(base64.b64decode(image_string[22:])))

        text = "{}".format(
            pytesseract.image_to_string(img, lang="eng", config="--psm 11 oem 2")
            # pytesseract.image_to_string(img, lang="eng", config="--psm 6")
        )
        results = pytesseract.image_to_data(img, output_type=output.DICT)
        # keys= results.keys()
      
        # print(results.keys())
        new_text = text.split()
        new_text1 = "\n".join([f'* {x}' for x in new_text])
        df = pd.DataFrame(results)
        df = df[df["word_num"] != 0]
        new_results =df["text"].tolist()
        new_results = "\n".join([f'* {x}' for x in new_results])
        print(new_text)

        # for i in range(0, len(results["text"])):
            # extract the bounding box coordinates of the text region from
            # the current result

            # x = results["left"][i]
            # y = results["top"][i]
            # w = results["width"][i]
            # h = results["height"][i]
            # text1 = results["text"][i]
            # conf = int(results["conf"][i])
            # if 
            # print(f"Count {i}", text1)
       
        
        return new_text, new_results
    else:
        raise PreventUpdate
            





if __name__ == "__main__":
    app.run_server(debug=True)