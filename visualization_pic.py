import os
import geopandas as gpd
from shapely.geometry import LineString
import matplotlib.pyplot as plt
from lxml import etree


def extract_lines_from_kml_simple(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = etree.parse(f)

    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    coords_elements = tree.xpath('//kml:LineString/kml:coordinates', namespaces=ns)

    lines = []
    for elem in coords_elements:
        coord_text = elem.text.strip()
        coord_pairs = coord_text.split()
        coords = [(float(c.split(',')[0]), float(c.split(',')[1])) for c in coord_pairs if ',' in c]
        if len(coords) >= 2:
            lines.append(LineString(coords))

    print(f"从 {os.path.basename(file_path)} 提取 LineString 数: {len(lines)}")
    return lines


def main():
    kml_folder = r"./"   # 更换自己的KML文件路径
    china_geojson = r"CHN.json"    # 更换自己的中国地图底图路径
    output_image = "railway_trace_map.png"

    kml_files = [os.path.join(kml_folder, f) for f in os.listdir(kml_folder) if f.endswith('.kml')]

    all_lines = []
    for kml_file in kml_files:
        lines = extract_lines_from_kml_simple(kml_file)
        all_lines.extend(lines)

    if not all_lines:
        print("没有解析到任何线路，程序终止。")
        return

    gdf_lines = gpd.GeoDataFrame(geometry=all_lines, crs="EPSG:4326")

    china = gpd.read_file(china_geojson)
    china = china.to_crs("EPSG:4326")

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 替换为你电脑支持的中文字体
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(20, 20))
    china.plot(ax=ax, color='#222222', edgecolor='white')
    gdf_lines.plot(ax=ax, color='orange', linewidth=4)
    ax.set_title('铁路足迹', fontsize=20,color='white')
    ax.axis('off')

    plt.savefig(output_image, dpi=300, bbox_inches='tight')
    print(f"地图已保存为 {output_image}")
    #plt.show()


if __name__ == "__main__":
    main()
