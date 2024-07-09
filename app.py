# -*- coding: utf-8 -*-
import base64
import io
import json
import re

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# 日本語フォントの設定
font_path = "SawarabiMincho-Regular.ttf"  # フォントファイルのパス
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

def parse_equation(equation, x):
    # 絶対値記号を含む式を処理する関数
    if '|' in equation:
        parts = equation.split('|')
        inner_eq = parts[1].strip()
        return np.abs(parse_linear_equation(inner_eq, x))
    else:
        return parse_linear_equation(equation, x)

def parse_linear_equation(equation, x):
    # ax + b 形式の線形方程式を解析する関数
    equation = equation.replace(' ', '')  # スペースを削除
    if 'x' not in equation:
        return float(equation) * np.ones_like(x)

    parts = re.findall(r'([+-]?\d*\.?\d*x?)', equation)
    parts = [p for p in parts if p]  # 空の要素を削除

    a, b = 0, 0
    for part in parts:
        if 'x' in part:
            coef = part.replace('x', '')
            if coef in ['+', '-']:
                a += 1 if coef == '+' else -1
            elif coef == '':
                a += 1
            else:
                a += float(coef)
        else:
            b += float(part)

    return a * x + b

def create_graph(graph_data):
    fig, ax = plt.subplots(figsize=(10, 8))
    graph_type = graph_data.get('graph_type', 'linear')
    equation = graph_data.get('equation', '')
    x_min = graph_data.get('x_min', -10)
    x_max = graph_data.get('x_max', 10)
    y_min = graph_data.get('y_min', -10)
    y_max = graph_data.get('y_max', 10)

    x = np.linspace(x_min, x_max, 1000)

    if graph_type == 'linear':
        if equation.startswith('y = '):
            equation = equation[4:]  # 'y = ' を削除
        y = parse_equation(equation, x)
    else:
        # 他のグラフタイプの処理（必要に応じて追加）
        y = x  # デフォルトの直線

    ax.plot(x, y)
    ax.set_title(graph_data.get('equation', ''), fontsize=16, fontproperties=font_prop)
    ax.set_xlabel('x', fontsize=12, fontproperties=font_prop)
    ax.set_ylabel('y', fontsize=12, fontproperties=font_prop)
    ax.grid(True)

    # x軸とy軸を太線に設定
    ax.axhline(y=0, color='k', linewidth=2)
    ax.axvline(x=0, color='k', linewidth=2)

    # メモリを1ずつに設定
    ax.xaxis.set_major_locator(plt.MultipleLocator(1))
    ax.yaxis.set_major_locator(plt.MultipleLocator(1))

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

    # JSONパラメータの入力
    json_input = st.text_area("JSONパラメータを入力してください", height=300)

    if st.button("グラフ生成"):
        try:
            data = json.loads(json_input)
            graphs = data.get('graphs', [])

            images = []
            for graph_data in graphs:
                fig = create_graph(graph_data)
                img_str = get_image_base64(fig)
                images.append(img_str)
                plt.close(fig)  # メモリリークを防ぐためにfigureを閉じる

            # 結果をJSONで返す
            result = {
                "images": images
            }
            st.json(result)

            # 画像の表示（オプション）
            for i, img_str in enumerate(images):
                st.image(f"data:image/png;base64,{img_str}", caption=f"Graph {i + 1}")

        except json.JSONDecodeError:
            st.error("無効なJSONフォーマットです。正しいJSONを入力してください。")
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()