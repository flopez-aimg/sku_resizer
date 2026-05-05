import streamlit as st
from PIL import Image
import zipfile
import io
import os

# Configuración de la página
st.set_page_config(page_title="SKU Image Resizer", page_icon="🖼️")

# --- Lógica de Reset ---
def clear_all():
    st.session_state["uploader_key"] += 1  # Incrementa la clave para forzar el reset del widget
    st.rerun() # Recarga la app

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

st.title("🖼️ SKU Image Resizer")
st.write("Sube tus imágenes, ajusta el tamaño y descarga todo en un ZIP.")

# 1. Parámetros de diseño en la barra lateral
with st.sidebar:
    st.header("Configuración")
    target_w = st.number_input("Ancho Base (px)", value=500)
    target_h = st.number_input("Altura (px)", value=375)
    quality = st.slider("Calidad JPG", 10, 100, 90)
    
    st.markdown("---")
    # BOTÓN CLEAR
    if st.button("🗑️ Limpiar Todo", help="Borra las imágenes y resetea la app"):
        clear_all()

# 2. Selector de archivos (usando la clave dinámica para resetearlo)
uploaded_files = st.file_uploader("Selecciona las imágenes de tu PC", 
                                  accept_multiple_files=True, 
                                  type=['png', 'jpg', 'jpeg', 'webp'],
                                  key=f"uploader_{st.session_state['uploader_key']}")

if st.button("🚀 Convertir Imágenes"):
    if not uploaded_files:
        st.error("Por favor, sube al menos una imagen.")
    else:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            progress_bar = st.progress(0)
            
            for i, file in enumerate(uploaded_files):
                img = Image.open(file)
                original_format = img.format 
                
                # Determinar modo y fondo
                if img.mode in ("RGBA", "LA") or (original_format in ["PNG", "WEBP"]):
                    mode = "RGBA"
                    bg_color = (0, 0, 0, 0) 
                else:
                    mode = "RGB"
                    bg_color = (255, 255, 255) 
                
                img = img.convert(mode)

                # Redimensionar proporcional
                w, h = img.size
                aspect_ratio = w / h
                new_width = int(target_h * aspect_ratio)
                
                if new_width > target_w:
                    new_width = target_w
                    new_height = int(target_w / aspect_ratio)
                else:
                    new_height = target_h
                
                img_resized = img.resize((new_width, new_height), Image.LANCZOS)

                # Crear lienzo final y centrar
                final_img = Image.new(mode, (target_w, target_h), bg_color)
                x_offset = (target_w - new_width) // 2
                y_offset = (target_h - new_height) // 2
                
                mask = img_resized if mode == "RGBA" else None
                final_img.paste(img_resized, (x_offset, y_offset), mask)

                # Guardar en el buffer
                img_io = io.BytesIO()
                if mode == "RGBA":
                    final_img.save(img_io, "PNG")
                    ext = ".png"
                else:
                    final_img.save(img_io, "JPEG", quality=quality)
                    ext = ".jpg"
                
                clean_name = os.path.splitext(file.name)[0] + ext
                zip_file.writestr(clean_name, img_io.getvalue())
                
                progress_bar.progress((i + 1) / len(uploaded_files))

        st.success("¡Proceso completado!")
        st.download_button(
            label="📁 Descargar todas las imágenes (.ZIP)",
            data=zip_buffer.getvalue(),
            file_name="imagenes_finales.zip",
            mime="application/zip"
        )