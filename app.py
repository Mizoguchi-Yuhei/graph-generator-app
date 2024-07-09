# -*- coding: utf-8 -*-
import base64
import io
import json

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# 日本語フォントの設定
font_path = "SawarabiMincho-Regular.ttf"  # フォントファイルのパス
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()


def create_graph(graph_data):
    fig, ax = plt.subplots(figsize=(10, 8))
    graph_type = graph_data.get('graph_type', 'linear')
    equation = graph_data.get('equation', '')
    x_min = graph_data.get('x_min', -10)
    x_max = graph_data.get('x_max', 10)
    y_min = graph_data.get('y_min', -10)
    y_max = graph_data.get('y_max', 10)
    coefficients = graph_data.get('coefficients', {})

    x = np.linspace(x_min, x_max, 1000)

    if graph_type == 'linear':
        if equation.startswith('y = |'):
            # 絶対値関数の処理
            inner_eq = equation[5:-1]  # '|' の中身を取得
            y = np.abs(eval(inner_eq))
        else:
            # 通常の線形関数の処理
            a = coefficients.get('a', 1)
            b = coefficients.get('b', 0)
            y = a * x + b

    ax.plot(x, y)
    ax.set_title(equation, fontsize=16, fontproperties=font_prop)
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