import streamlit as st
from PIL import Image
import zipfile
import io
import os

# 1. Configuración de la página
st.set_page_config(page_title="SKU Image Resizer Pro", page_icon="🖼️", layout="centered")

# 2. CSS para Microanimaciones, Estilo Premium y Personalización de Colores
st.markdown("""
    <style>
    /* Animación de entrada suave */
    .main {
        animation: fadeIn 0.8s ease-in-out;
    }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    /* ESTILO ESPECÍFICO PARA EL BOTÓN DE CONVERTIR (Primary Button) */
    div.stButton > button[kind="primary"] {
        background-color: #d1f2d1 !important; /* Verde muy clarito */
        color: #1a5c1a !important;           /* Verde oscuro */
        border: 1px solid #b2e0b2 !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        height: 3em !important;
    }
    
    div.stButton > button[kind="primary"]:hover {
        background-color: #b2e0b2 !important; /* Un toque más oscuro al pasar el mouse */
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1) !important;
    }

    /* Estilo para los demás botones (Secundarios) */
    .stButton>button {
        transition: all 0.3s ease;
        border-radius: 10px;
    }
    
    /* Personalización del área de carga */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #4CAF50;
        border-radius: 15px;
        background-color: #f9fff9;
        transition: background-color 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Lógica de Reset de Estado
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

def clear_all():
    st.session_state["uploader_key"] += 1
    st.rerun()

# --- INTERFAZ DE USUARIO ---

st.title("🖼️ SKU Image Resizer")
st.write("Optimiza tus SKUs en segundos: ajusta tamaño, centra y mantén transparencias.")

# Barra lateral de configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    target_w = st.number_input("Ancho Base (px)", value=500)
    target_h = st.number_input("Altura (px)", value=375)
    quality = st.slider("Calidad JPG", 10, 100, 90)
    
    st.markdown("---")
    if st.button("🗑️ Limpiar Todo", use_container_width=True):
        clear_all()
    st.caption("v1.3 - UI Personalizada")

# Área de carga principal
st.markdown("### 📂 Carga de trabajo")
uploaded_files = st.file_uploader(
    "Arrastrá o seleccioaná tus archivos para convertir. Si querés convertir una carpeta entera, buscala en tu PC y arrastrala.", 
    accept_multiple_files=True, 
    type=['png', 'jpg', 'jpeg', 'webp'],
    key=f"uploader_{st.session_state['uploader_key']}"
)

# Botón de acción (Mantenemos type="primary" para que tome los colores verdes del CSS arriba)
if st.button("🚀 Convertir Imágenes", use_container_width=True, type="primary"):
    if not uploaded_files:
        st.warning("⚠️ Primero selecciona o arrastra algunas imágenes.")
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
            
            status_text.text("✅ ¡Procesamiento completado!")

        st.success(f"¡Listo! Se han procesado {len(uploaded_files)} imágenes.")
        st.download_button(
            label="📁 Descargar Pack de Imágenes (.ZIP)",
            data=zip_buffer.getvalue(),
            file_name="skus_convertidos.zip",
            mime="application/zip",
            use_container_width=True
        )
