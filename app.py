import random
import io
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Painel de Live TikTok", page_icon="🎥", layout="wide")

st.title("🎥 Painel de Live TikTok")

aba_metas, aba_roleta, aba_banner = st.tabs(
    ["🎯 Metas de Presentes", "🎡 Roleta", "🖼️ Criador de Banner"]
)

# =========================================================
# ABA 1 - PAINEL DE METAS COM NÍVEIS
# =========================================================
with aba_metas:
    st.subheader("Metas de presentes por nível")
    st.caption("Configure os níveis e vá atualizando o total durante a live.")

    if "niveis" not in st.session_state:
        st.session_state.niveis = [
            {"nome": "Nível 1", "meta": 50},
            {"nome": "Nível 2", "meta": 150},
            {"nome": "Nível 3", "meta": 300},
        ]

    with st.expander("⚙️ Configurar níveis"):
        for i, nivel in enumerate(st.session_state.niveis):
            c1, c2, c3 = st.columns([3, 2, 1])
            nivel["nome"] = c1.text_input("Nome", nivel["nome"], key=f"nome_{i}")
            nivel["meta"] = c2.number_input(
                "Meta (presentes)", min_value=1, value=nivel["meta"], key=f"meta_{i}"
            )
            if c3.button("🗑️", key=f"del_{i}"):
                st.session_state.niveis.pop(i)
                st.rerun()

        if st.button("➕ Adicionar nível"):
            st.session_state.niveis.append(
                {"nome": f"Nível {len(st.session_state.niveis) + 1}", "meta": 100}
            )
            st.rerun()

    st.divider()

    total_atual = st.number_input(
        "🎁 Total de presentes recebidos até agora", min_value=0, value=0, step=1
    )

    st.divider()

    niveis_ordenados = sorted(st.session_state.niveis, key=lambda n: n["meta"])
    for nivel in niveis_ordenados:
        progresso = min(total_atual / nivel["meta"], 1.0)
        atingido = total_atual >= nivel["meta"]
        emoji = "✅" if atingido else "🔒"
        st.markdown(f"**{emoji} {nivel['nome']}** — {total_atual}/{nivel['meta']}")
        st.progress(progresso)

# =========================================================
# ABA 2 - ROLETA
# =========================================================
with aba_roleta:
    st.subheader("Roleta de dinâmica ao vivo")
    st.caption("Cadastre os itens (desafios, perguntas, prêmios) e sorteie na hora.")

    texto_itens = st.text_area(
        "Um item por linha",
        value="Cante uma música\nConte uma piada\nMostre o pet\nDance 10 segundos\nResponda uma pergunta do chat",
        height=150,
    )
    itens = [linha.strip() for linha in texto_itens.split("\n") if linha.strip()]

    if st.button("🎲 Girar a roleta", type="primary"):
        if itens:
            st.session_state.resultado_roleta = random.choice(itens)
        else:
            st.warning("Adicione pelo menos um item.")

    if "resultado_roleta" in st.session_state:
        st.markdown(
            f"""
            <div style="
                text-align:center;
                padding: 40px;
                border-radius: 16px;
                background: linear-gradient(135deg, #ff2b54, #ff7a00);
                color: white;
                font-size: 32px;
                font-weight: bold;
                margin-top: 20px;">
                🎉 {st.session_state.resultado_roleta}
            </div>
            """,
            unsafe_allow_html=True,
        )

# =========================================================
# ABA 3 - CRIADOR DE BANNER
# =========================================================
with aba_banner:
    st.subheader("Criador de banner de fundo")

    col_config, col_preview = st.columns([1, 1.3])

    with col_config:
        titulo = st.text_input("Título / Nome", "Sua Live Começou!")
        subtitulo = st.text_input("Subtítulo / Tema", "Vem trocar ideia comigo")
        redes = st.text_input("Redes sociais (opcional)", "@seuusuario")

        cor_fundo_inicio = st.color_picker("Cor de fundo (início)", "#1a1a2e")
        cor_fundo_fim = st.color_picker("Cor de fundo (fim)", "#e94560")
        cor_texto = st.color_picker("Cor do texto", "#ffffff")

        largura = st.selectbox("Formato", ["1080x1920 (vertical)", "1920x1080 (horizontal)"])

    def gerar_gradiente(largura, altura, cor1, cor2):
        img = Image.new("RGB", (largura, altura), cor1)
        draw = ImageDraw.Draw(img)
        c1 = tuple(int(cor1.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        c2 = tuple(int(cor2.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        for y in range(altura):
            t = y / altura
            cor = tuple(int(c1[j] + (c2[j] - c1[j]) * t) for j in range(3))
            draw.line([(0, y), (largura, y)], fill=cor)
        return img

    def carregar_fonte(tamanho):
        caminhos = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for caminho in caminhos:
            try:
                return ImageFont.truetype(caminho, tamanho)
            except Exception:
                continue
        return ImageFont.load_default()

    def centralizar_texto(draw, texto, y, largura_img, fonte, cor):
        bbox = draw.textbbox((0, 0), texto, font=fonte)
        largura_texto = bbox[2] - bbox[0]
        x = (largura_img - largura_texto) / 2
        draw.text((x, y), texto, font=fonte, fill=cor)

    if largura.startswith("1080"):
        w, h = 1080, 1920
    else:
        w, h = 1920, 1080

    banner = gerar_gradiente(w, h, cor_fundo_inicio, cor_fundo_fim)
    draw = ImageDraw.Draw(banner)

    fonte_titulo = carregar_fonte(int(h * 0.07))
    fonte_subtitulo = carregar_fonte(int(h * 0.035))
    fonte_redes = carregar_fonte(int(h * 0.03))

    centralizar_texto(draw, titulo, h * 0.42, w, fonte_titulo, cor_texto)
    centralizar_texto(draw, subtitulo, h * 0.50, w, fonte_subtitulo, cor_texto)
    if redes.strip():
        centralizar_texto(draw, redes, h * 0.90, w, fonte_redes, cor_texto)

    with col_preview:
        st.image(banner, use_container_width=True)

        buffer = io.BytesIO()
        banner.save(buffer, format="PNG")
        st.download_button(
            "⬇️ Baixar banner",
            data=buffer.getvalue(),
            file_name="banner_live.png",
            mime="image/png",
        )
