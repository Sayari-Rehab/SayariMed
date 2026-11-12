"""
ui/pwa.py
---------
Metaetiquetas PWA para que Sayari Med se pueda instalar en iPad/iPhone/Android.

Al abrir la app en el móvil/iPad:
- Safari → Compartir → "Añadir a pantalla de inicio".
- Chrome Android → Menú → "Instalar aplicación".

Se verá como app nativa: sin barra de URL, con ícono propio.
"""

import streamlit as st
import streamlit.components.v1 as components


def inyectar_pwa() -> None:
    """
    Inyecta metaetiquetas PWA en el <head> del documento.

    Nota: como Streamlit no permite manipular directamente el <head>,
    usamos un truco con components.v1.html + JavaScript.
    """
    components.html(
        """
        <script>
        (function() {
            const parentDoc = window.parent.document;

            // ---- Evitar duplicados ----
            if (parentDoc.querySelector('link[rel="manifest"]')) return;

            // ---- Meta tag: theme color ----
            let metaTheme = parentDoc.createElement('meta');
            metaTheme.setAttribute('name', 'theme-color');
            metaTheme.setAttribute('content', '#112240');
            parentDoc.head.appendChild(metaTheme);

            // ---- Meta tag: viewport optimizado para móvil ----
            let metaViewport = parentDoc.querySelector('meta[name="viewport"]');
            if (metaViewport) {
                metaViewport.setAttribute(
                    'content',
                    'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no'
                );
            }

            // ---- Meta tags: iOS ----
            let metaAppleCapable = parentDoc.createElement('meta');
            metaAppleCapable.setAttribute('name', 'apple-mobile-web-app-capable');
            metaAppleCapable.setAttribute('content', 'yes');
            parentDoc.head.appendChild(metaAppleCapable);

            let metaAppleStatus = parentDoc.createElement('meta');
            metaAppleStatus.setAttribute('name', 'apple-mobile-web-app-status-bar-style');
            metaAppleStatus.setAttribute('content', 'black-translucent');
            parentDoc.head.appendChild(metaAppleStatus);

            let metaAppleTitle = parentDoc.createElement('meta');
            metaAppleTitle.setAttribute('name', 'apple-mobile-web-app-title');
            metaAppleTitle.setAttribute('content', 'Sayari Med');
            parentDoc.head.appendChild(metaAppleTitle);

            // ---- Meta tags: Android ----
            let metaMobileCapable = parentDoc.createElement('meta');
            metaMobileCapable.setAttribute('name', 'mobile-web-app-capable');
            metaMobileCapable.setAttribute('content', 'yes');
            parentDoc.head.appendChild(metaMobileCapable);

            // ---- Manifest PWA (data-URI para no necesitar archivo externo) ----
            const manifest = {
                "name": "Sayari Med",
                "short_name": "Sayari",
                "description": "Sistema Integral de Gestión Clínica & Fisioterapia",
                "start_url": ".",
                "display": "standalone",
                "orientation": "portrait",
                "background_color": "#112240",
                "theme_color": "#112240",
                "icons": [
                    {
                        "src": "/app/static/logo_favicon.png",
                        "sizes": "192x192",
                        "type": "image/png",
                        "purpose": "any maskable"
                    },
                    {
                        "src": "/app/static/logo_favicon.png",
                        "sizes": "512x512",
                        "type": "image/png",
                        "purpose": "any maskable"
                    }
                ]
            };

            const manifestBlob = new Blob([JSON.stringify(manifest)], {type: 'application/json'});
            const manifestURL = URL.createObjectURL(manifestBlob);
            let linkManifest = parentDoc.createElement('link');
            linkManifest.setAttribute('rel', 'manifest');
            linkManifest.setAttribute('href', manifestURL);
            parentDoc.head.appendChild(linkManifest);

            // ---- Apple touch icon ----
            let linkIcon = parentDoc.createElement('link');
            linkIcon.setAttribute('rel', 'apple-touch-icon');
            linkIcon.setAttribute('href', '/app/static/logo_favicon.png');
            parentDoc.head.appendChild(linkIcon);
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def mostrar_banner_instalacion() -> None:
    """
    Muestra un pequeño banner con instrucciones para instalar como app
    (solo la primera vez que se abre en móvil/tablet).
    """
    if "pwa_banner_mostrado" in st.session_state:
        return

    st.markdown(
        """
        <div style="
            background: linear-gradient(90deg, #112240 0%, #1A2E5A 100%);
            color: #FFFFFF;
            padding: 0.8rem 1.2rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            font-size: 0.9rem;
            border-left: 4px solid #C9A961;
        ">
            💡 <b>Tip:</b> Para usar Sayari Med como app nativa, en iPad/iPhone abre
            <b>Compartir → Añadir a pantalla de inicio</b>. En Android: <b>Menú → Instalar aplicación</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state["pwa_banner_mostrado"] = True