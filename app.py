import streamlit as st
import socket
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="ポート調査ツール", layout="centered")

# --- カスタムCSS ---
st.markdown("""
    <style>
    .credit { text-align: right; font-size: 14px; color: #666; margin-bottom: -20px; }
    .stTextInput label, .stMultiSelect label { font-size: 20px !important; color: #7c3aed !important; font-weight: bold !important; }
    .status-open { color: #22c55e; font-weight: bold; }
    .status-closed { color: #ef4444; }
    .result-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    .result-table th, .result-table td { border: 1px solid #ddd; padding: 12px; text-align: left; }
    .result-table th { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="credit">開発/制作：緒方</p>', unsafe_allow_html=True)
st.title("🔍 ポートスキャンツール")
st.write("指定したホストのポート開放状況を確認します。")
st.markdown("---")

# --- 設定セクション ---
col1, col2 = st.columns([2, 1])
with col1:
    target = st.text_input("対象ホスト (IPまたはホスト名)", value="127.0.0.1", help="例: 192.168.1.1 や google.com")
with col2:
    timeout = st.number_input("タイムアウト(秒)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)

# よく使うポートのプリセット
common_ports = {
    "21 (FTP)": 21,
    "22 (SSH)": 22,
    "23 (Telnet)": 23,
    "25 (SMTP)": 25,
    "53 (DNS)": 53,
    "80 (HTTP)": 80,
    "110 (POP3)": 110,
    "443 (HTTPS)": 443,
    "445 (SMB)": 445,
    "3389 (RDP)": 3389,
    "8080 (Proxy/Alt HTTP)": 8080
}

selected_labels = st.multiselect(
    "調査するポートを選択（直接入力も可能）",
    options=list(common_ports.keys()),
    default=["80 (HTTP)", "443 (HTTPS)"]
)

# 直接入力用のテキストエリア
custom_ports_raw = st.text_input("追加で調査するポート番号 (カンマ区切り)", help="例: 5000, 8000, 161")

# --- スキャン実行 ---
if st.button("スキャン開始", use_container_width=True):
    # 調査対象ポートの整理
    port_list = [common_ports[label] for label in selected_labels]
    if custom_ports_raw:
        try:
            custom_ports = [int(p.strip()) for p in custom_ports_raw.split(",") if p.strip().isdigit()]
            port_list.extend(custom_ports)
        except:
            st.error("追加ポートの入力形式が正しくありません。")
    
    port_list = sorted(list(set(port_list))) # 重複排除とソート

    if not target:
        st.error("ホスト名を入力してください。")
    elif not port_list:
        st.warning("調査するポートを少なくとも1つ選択または入力してください。")
    else:
        st.info(f"🚀 {target} のスキャンを開始しました...")
        
        results = []
        progress_bar = st.progress(0)
        
        for i, port in enumerate(port_list):
            # 進捗表示
            progress_bar.progress((i + 1) / len(port_list))
            
            try:
                # ソケット通信試行
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((target, port))
                
                if result == 0:
                    results.append({"port": port, "status": "OPEN", "color": "status-open"})
                else:
                    results.append({"port": port, "status": "CLOSED", "color": "status-closed"})
                sock.close()
            except Exception as e:
                results.append({"port": port, "status": f"ERROR", "color": "status-closed"})

        # --- 結果表示 ---
        st.markdown("### 📊 調査結果")
        
        html_table = '<table class="result-table"><tr><th>ポート</th><th>状態</th></tr>'
        for res in results:
            html_table += f'<tr><td>{res["port"]}</td><td class="{res["color"]}">{res["status"]}</td></tr>'
        html_table += '</table>'
        
        st.markdown(html_table, unsafe_allow_html=True)
        
        st.success(f"スキャン完了: {datetime.now().strftime('%H:%M:%S')}")


