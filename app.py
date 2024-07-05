# -*- coding: utf-8 -*-
import base64
import io
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.ticker import MaxNLocator
from scipy import integrate
from fractions import Fraction
import matplotlib.font_manager as fm

# 日本語フォントの設定
font_path = "ipaexg.ttf"  # フォントファイルのパス
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

def parse_fraction(s):
    try:
        return float(sum(Fraction(term) for term in s.replace(' ', '').split('+')))
    except ValueError:
        st.error(f"無効な入力: {s}. 数値または分数 (例: 1/2) を入力してください。")
        return 0

def create_graph(data):
    fig, ax = plt.subplots(figsize=(10, 8))
    graph_type = data.get('type', 'linear')

    x_min = data.get('x_min', -10)
    x_max = data.get('x_max', 10)
    y_min = data.get('y_min', -10)
    y_max = data.get('y_max', 10)
    x = np.linspace(x_min, x_max, 1000)

    plot_functions = {
        'polynomial': lambda: np.polyval(data['coefficients'], x),
        'sin': lambda: data['amplitude'] * np.sin(data['frequency'] * x),
        'cos': lambda: data['amplitude'] * np.cos(data['frequency'] * x),
        'derivative': lambda: np.gradient(np.polyval(data['coefficients'], x), x),
        'integral': lambda: integrate.cumtrapz(np.polyval(data['coefficients'], x), x, initial=0),
        'linear': lambda: data['y']
    }

    if graph_type in plot_functions:
        y = plot_functions[graph_type]()
        ax.plot(x, y)
    elif graph_type in ['circle', 'sector']:
        shape = plt.Circle((0, 0), data['radius'], fill=False) if graph_type == 'circle' else \
            plt.Wedge((0, 0), data['radius'], data['start_angle'], data['end_angle'], fill=False)
        ax.add_artist(shape)
        ax.set_xlim(-data['radius'] - 1, data['radius'] + 1)
        ax.set_ylim(-data['radius'] - 1, data['radius'] + 1)
        ax.set_aspect('equal')

    # タイトルの設定（日本語対応）
    if graph_type == 'polynomial':
        title = f"{data['degree']}次関数"
    elif graph_type == 'sin':
        title = "正弦関数"
    elif graph_type == 'cos':
        title = "余弦関数"
    elif graph_type == 'derivative':
        title = "導関数"
    elif graph_type == 'integral':
        title = "積分関数"
    elif graph_type == 'circle':
        title = "円"
    elif graph_type == 'sector':
        title = "扇形"
    else:
        title = "線形関数"

    ax.set_title(title, fontsize=16, fontproperties=font_prop)
    ax.set_xlabel(data['xlabel'], fontsize=12, fontproperties=font_prop)
    ax.set_ylabel(data['ylabel'], fontsize=12, fontproperties=font_prop)
    ax.grid(True)

    # x軸とy軸を太線に設定
    ax.axhline(y=0, color='k', linewidth=2)
    ax.axvline(x=0, color='k', linewidth=2)

    # メモリを1ずつに設定
    ax.xaxis.set_major_locator(plt.MultipleLocator(1))
    ax.yaxis.set_major_locator(plt.MultipleLocator(1))

    # x軸とy軸の範囲を設定
    if graph_type not in ['circle', 'sector']:
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

    plt.tight_layout()
    return fig

def get_image_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode()

def main():
    st.set_page_config(page_title="グラフ生成", page_icon="📊")
    st.title("グラフ生成")

    graph_types = ["polynomial", "sin", "cos", "derivative", "integral", "circle", "sector", "linear"]
    graph_type = st.selectbox("グラフの種類を選択", graph_types)

    data = {'type': graph_type, 'xlabel': "x", 'ylabel': "y"}

    if graph_type == "polynomial":
        data['degree'] = st.number_input("次数", min_value=1, max_value=5, value=2)
        data['coefficients'] = [parse_fraction(st.text_input(f"{i}次の係数", value="1" if i == data['degree'] else "0")) for i in range(data['degree'], -1, -1)]
    elif graph_type in ["derivative", "integral"]:
        data['coefficients'] = [parse_fraction(st.text_input(f"{i}次の係数", value="1" if i == 2 else "0")) for i in range(2, -1, -1)]
    elif graph_type in ["sin", "cos"]:
        data['amplitude'] = parse_fraction(st.text_input("振幅", value="1"))
        data['frequency'] = parse_fraction(st.text_input("周波数", value="1"))

    if graph_type not in ["circle", "sector"]:
        data['x_min'] = parse_fraction(st.text_input("x最小値", value="-10"))
        data['x_max'] = parse_fraction(st.text_input("x最大値", value="10"))
        data['y_min'] = parse_fraction(st.text_input("y最小値", value="-10"))
        data['y_max'] = parse_fraction(st.text_input("y最大値", value="10"))

    if graph_type in ["circle", "sector"]:
        data['radius'] = parse_fraction(st.text_input("半径", value="1"))
        if graph_type == "sector":
            data['start_angle'] = parse_fraction(st.text_input("開始角度", value="0"))
            data['end_angle'] = parse_fraction(st.text_input("終了角度", value="90"))

    if graph_type == "linear":
        data['x'] = [parse_fraction(x) for x in st.text_input("xの値（カンマ区切り）", "1,2,3,4,5").split(',')]
        data['y'] = [parse_fraction(y) for y in st.text_input("yの値（カンマ区切り）", "1,4,9,16,25").split(',')]

    data['xlabel'] = st.text_input("x軸ラベル", "x")
    data['ylabel'] = st.text_input("y軸ラベル", "y")

    if st.button("グラフ生成"):
        fig = create_graph(data)
        st.pyplot(fig)

        img_str = get_image_base64(fig)
        st.session_state['graph_image'] = img_str

if __name__ == "__main__":
    main()
