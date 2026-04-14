import warnings

class Backend():
    """This is a template of Backend, does not have any actual function."""

    def __init__(self):
        """Here goes the backend's metadata. In template, APIs are also aliased here."""
        self.name = "template"
        self.friendly_name = "No available backend"
        self.version = "0.0.0"
        self.author = []

        # Make placeholders for APIs
        func = self.placeholder_function # Just for aliasing

        self.window_create = func               # Create win
        self.window_set_title = func            # Set window title
        self.window_set_icon = func             # Set window icon
        self.window_set_size = func             # Set window size
        self.window_set_scale_mode = func       # Set window DPI scale mode
        self.window_set_background = func       # Set window background
        self.window_set_alpha = func            # Set window transparency
        self.window_set_state = func            # Set window state (e.g. minimized / normal)
        self.window_set_fullscreen = func       # Set if window fullscreen
        self.window_set_titlebar = func         # Set window titlebar state (Shown / Hidden)
        self.window_edit = func                 # Edit other window properties provided by backend

    def placeholder_function(self, *args, **kwargs):
        warnings.warn(f"This function is not implemented in backend {self.friendly_name}.")