"""Android WebView wrapper for the single-file Telegram Nick Finder app.

Build with Buildozer. On Android this opens ``index.html`` inside a native
WebView with JavaScript, DOM storage and file access enabled. On desktop it
shows a small Kivy fallback and can be used for smoke checks.
"""

from pathlib import Path
from urllib.parse import quote
import webbrowser

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


APP_DIR = Path(__file__).resolve().parent
INDEX_FILE = APP_DIR / "index.html"


class NickFinderApp(App):
    """Small Kivy shell that delegates the UI to the bundled HTML app."""

    title = "Telegram Nick Finder"

    def build(self):
        Window.clearcolor = (0.03, 0.07, 0.13, 1)
        root = BoxLayout(orientation="vertical", padding=24, spacing=16)
        label = Label(
            text=(
                "Telegram Nick Finder\n\n"
                "Android buildda index.html WebView ichida ochiladi.\n"
                "Desktop tekshiruvda esa brauzer orqali ochishingiz mumkin."
            ),
            halign="center",
            valign="middle",
        )
        label.bind(size=label.setter("text_size"))
        root.add_widget(label)
        open_button = Button(text="index.html ni brauzerda ochish", size_hint_y=None, height=54)
        open_button.bind(on_release=lambda *_: webbrowser.open(INDEX_FILE.as_uri()))
        root.add_widget(open_button)
        Clock.schedule_once(self._open_android_webview, 0)
        return root

    def _open_android_webview(self, *_args):
        if not self._is_android():
            return

        from android.runnable import run_on_ui_thread
        from jnius import autoclass

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        WebView = autoclass("android.webkit.WebView")
        WebViewClient = autoclass("android.webkit.WebViewClient")
        WebChromeClient = autoclass("android.webkit.WebChromeClient")
        ViewGroupLayoutParams = autoclass("android.view.ViewGroup$LayoutParams")

        activity = PythonActivity.mActivity
        html_url = "file://" + quote(str(INDEX_FILE))

        @run_on_ui_thread
        def attach_webview():
            webview = WebView(activity)
            settings = webview.getSettings()
            settings.setJavaScriptEnabled(True)
            settings.setDomStorageEnabled(True)
            settings.setAllowFileAccess(True)
            settings.setAllowContentAccess(True)
            settings.setDatabaseEnabled(True)
            settings.setMediaPlaybackRequiresUserGesture(False)
            webview.setWebViewClient(WebViewClient())
            webview.setWebChromeClient(WebChromeClient())
            webview.loadUrl(html_url)
            activity.setContentView(
                webview,
                ViewGroupLayoutParams(
                    ViewGroupLayoutParams.MATCH_PARENT,
                    ViewGroupLayoutParams.MATCH_PARENT,
                ),
            )
            self.webview = webview

        attach_webview()

    @staticmethod
    def _is_android():
        try:
            from kivy.utils import platform
        except ImportError:
            return False
        return platform == "android"


if __name__ == "__main__":
    NickFinderApp().run()
