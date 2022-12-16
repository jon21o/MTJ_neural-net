from bokeh.plotting import figure
from bokeh.models import LinearAxis, LogAxis, CategoricalAxis


def create_generic_fig(xaxis_label="", yaxis_label="", **options):
    """Create a simple Bokeh figure for plotting with nice looking settings"""
    # Specify the TOOLS and TOOLTIPS that should be included in the plot
    TOOLS = "tap, hover, pan, box_zoom, wheel_zoom, undo, reset, save"
    TOOLTIPS = [("index", "$index"), ("(x,y)", "($x, $y)")]

    # Allow for modifying figure properties from function call
    if "y_axis_type" in options:
        y_axis_type = options["y_axis_type"]
    else:
        y_axis_type = "auto"
    if "x_axis_type" in options:
        x_axis_type = options["x_axis_type"]
    else:
        x_axis_type = "auto"
    if "x_range" in options:
        x_range = options["x_range"]
    else:
        x_range = None
    if "y_range" in options:
        y_range = options["y_range"]
    else:
        y_range = None
    if "frame_height" in options:
        frame_height = options["frame_height"]
    else:
        frame_height = 700
    if "frame_width" in options:
        frame_width = options["frame_width"]
    else:
        frame_width = 700
    if "sizing_mode" in options:
        sizing_mode = options["sizing_mode"]
    else:
        sizing_mode = None

    # Initialize the figure to plot and return a handle to it
    fig = figure(
        output_backend="svg",
        x_range=x_range,
        y_range=y_range,
        tools=TOOLS,
        tooltips=TOOLTIPS,
        active_drag="pan",
        active_scroll="wheel_zoom",
        active_tap="tap",
        sizing_mode=sizing_mode,
        x_axis_type=x_axis_type,
        y_axis_type=y_axis_type,
    )

    # Set the size of the figure
    fig.frame_height = frame_height
    fig.frame_width = frame_width

    # Scale the text if needed
    if "scale_text" in options:
        scale_text = options["scale_text"]
        if scale_text == "width":
            text_scale = fig.frame_width
        elif scale_text == "height":
            text_scale = fig.frame_height
    else:
        text_scale = fig.frame_height

    # Set "default" properties and look of figure
    fig.min_border_top = 40
    fig.min_border_right = 40
    fig.min_border_bottom = 80
    fig.min_border_left = 80

    fig.xaxis.axis_label = str(xaxis_label)
    fig.yaxis.axis_label = str(yaxis_label)
    fig.xaxis.axis_label_text_font_size = "{}px".format(text_scale * (18 / 225))
    fig.yaxis.axis_label_text_font_size = "{}px".format(text_scale * (18 / 225))
    fig.xaxis.axis_label_text_baseline = "bottom"
    fig.yaxis.axis_label_text_baseline = "bottom"
    fig.yaxis.axis_label_standoff = 20
    fig.xaxis.axis_label_text_font = "Helvetica"
    fig.yaxis.axis_label_text_font = "Helvetica"
    fig.xaxis.axis_label_text_color = "black"
    fig.yaxis.axis_label_text_color = "black"
    fig.xaxis.axis_label_text_font_style = "normal"
    fig.yaxis.axis_label_text_font_style = "normal"
    fig.xaxis.major_label_text_font_size = "{}px".format(text_scale * (12 / 225))
    fig.yaxis.major_label_text_font_size = "{}px".format(text_scale * (12 / 225))
    fig.xaxis.major_label_text_color = "black"
    fig.yaxis.major_label_text_color = "black"
    fig.xaxis.major_label_standoff = 10
    fig.yaxis.major_label_standoff = 10

    # Make axis all-around figure - need to figure out what type of axis it is first
    if str(fig.xaxis[0]).startswith("LogAxis"):
        fig.add_layout(LogAxis(name="ax2above", major_label_text_font_size="0pt", ticker=fig.xaxis.ticker), "above")
    elif str(fig.xaxis[0]).startswith("CategoricalAxis"):
        fig.add_layout(CategoricalAxis(name="ax2above", major_label_text_font_size="0pt", ticker=fig.xaxis.ticker), "above")
    else:
        fig.add_layout(LinearAxis(name="ax2above", major_label_text_font_size="0pt", ticker=fig.xaxis.ticker), "above")

    if str(fig.yaxis[0]).startswith("LogAxis"):
        fig.add_layout(LogAxis(name="ax2above", major_label_text_font_size="0pt", ticker=fig.yaxis.ticker), "right")
    elif str(fig.yaxis[0]).startswith("CategoricalAxis"):
        fig.add_layout(CategoricalAxis(name="ax2above", major_label_text_font_size="0pt", ticker=fig.yaxis.ticker), "right")
    else:
        fig.add_layout(LinearAxis(name="ax2above", major_label_text_font_size="0pt", ticker=fig.yaxis.ticker), "right")

    fig.xaxis.axis_line_width = 3
    fig.yaxis.axis_line_width = 3
    fig.xaxis.axis_line_color = "black"
    fig.yaxis.axis_line_color = "black"
    fig.xaxis.major_tick_line_color = "black"
    fig.yaxis.major_tick_line_color = "black"
    fig.xaxis.minor_tick_line_color = None
    fig.yaxis.minor_tick_line_color = None
    fig.xaxis.major_tick_line_width = 3
    fig.yaxis.major_tick_line_width = 3
    fig.xaxis.minor_tick_line_width = 3
    fig.yaxis.minor_tick_line_width = 3
    fig.xaxis.major_tick_in = 0
    fig.yaxis.major_tick_in = 0
    fig.xaxis.major_tick_out = 20
    fig.yaxis.major_tick_out = 20
    fig.xaxis.minor_tick_in = 10
    fig.yaxis.minor_tick_in = 10
    fig.xaxis.minor_tick_out = 0
    fig.yaxis.minor_tick_out = 0
    fig.xgrid.grid_line_color = None
    fig.ygrid.grid_line_color = None
    fig.xaxis[0].major_tick_line_color = None
    fig.xaxis[0].major_label_text_color = None
    fig.xaxis[0].major_label_text_font_size = "0pt"
    fig.yaxis[1].major_tick_line_color = None
    fig.yaxis[1].major_label_text_color = None
    fig.yaxis[1].major_label_text_font_size = "0pt"

    # Modify the legend properties
    # fig.legend.label_text_font_size = "{}px".format(fig.frame_width * (12 / 225))
    # fig.legend.label_text_color = "black"
    # fig.legend.border_line_color = "black"
    # fig.legend.border_line_alpha = 1
    # fig.legend.border_line_width = 3
    # fig.legend.label_text_line_height = 2
    # fig.legend.glyph_height = int(fig.frame_width * (12 / 225))
    # fig.legend.glyph_width = int(fig.frame_width * (12 / 225))
    # fig.legend.margin = 30

    # Return the figure handle for modifying later if needed
    return fig
