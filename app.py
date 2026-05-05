import streamlit as st
from PIL import Image
import zipfile
import io
import os

# Configuración de la página
st.set_page_config(page_title="SKU Image Resizer", page_icon="🖼️")

# --- MICROANIMACIONES Y ESTILOS SUTILES ---
st.markdown("""
    <style>
    /* Animación de entrada para toda la app */
    .main {
        animation: fadeIn 0.8s ease-in-out;
    }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    /* Efecto suave en los botones */
    .stButton>button {
        transition: all 0.3s ease;
        border-radius: 8px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-color: #ff4b4b;
    }
    
    /* Estilo para el área de carga de archivos */
    [data-testid="stFileUploadDropzone"] {
        transition: all 0.3s ease;
        border: 2px dashed #ddd;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #ff4b4b;
        background-color: #fffafb;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE RESET ---
def clear_all():
    st.session_state["uploader_key"] += 1
    st.rerun()

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

st.title("🖼️ SKU Image Resizer")
st.write("Sube tus imágenes y déjanos el trabajo pesado a nosotros.")

# 1. Parámetros de diseño en la barra lateral
with st.sidebar:
    st.header("Configuración")
    target_w = st.number_input("Ancho Base (px)", value=500)
    target_h = st.number_input("Altura (px)", value=375)
    quality = st.slider("Calidad JPG", 10, 100, 90)
    
    st.markdown("---")
    if st.button("🗑️ Limpiar Todo"):
        clear_all()

# 2. Selector de archivos
uploaded_files = st.file_uploader("Selecciona las imágenes de tu PC", 
                                  accept_multiple_files=True, 
                                  type=['png', 'jpg', 'jpeg', 'webp'],
                                  key=f"uploader_{st.session_state['uploader_key']}")

if st.button("🚀 Convertir Imágenes", use_container_width=True):
    if not uploaded_files:
        st.error("Por favor, sube al menos una imagen.")
    else:
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Procesando: {file.name}")
                img = Image.open(file)
                original_format = img.format 
                
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

                final_img = Image.new(mode, (target_w, target_h), bg_color)
                x_offset = (target_w - new_width) // 2
                y_offset = (target_h - new_height) // 2
                
                mask = img_resized if mode == "RGBA" else None
                final_img.paste(img_resized, (x_offset, y_offset), mask)

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
            
            status_text.text("¡Todo listo!")

        st.success("¡Proceso completado con éxito!")
        st.download_button(
            label="📁 Descargar todas las imágenes (.ZIP)",
            data=zip_buffer.getvalue(),
            file_name="imagenes_finales.zip",
            mime="application/zip",
            use_container_width=True
        )
