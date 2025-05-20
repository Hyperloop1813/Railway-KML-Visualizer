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


def load_kml_lines(kml_folder):
    kml_files = [os.path.join(kml_folder, f) for f in os.listdir(kml_folder) if f.endswith('.kml')]
    all_lines = []
    for kml_file in kml_files:
        lines = extract_lines_from_kml_simple(kml_file)
        all_lines.extend(lines)

    if not all_lines:
        print("没有解析到任何线路，程序终止。")
        return None

    return gpd.GeoDataFrame(geometry=all_lines, crs="EPSG:4326")


def load_backgrounds(background_files):
    backgrounds = []
    for bg_file in background_files:
        bg = gpd.read_file(bg_file)
        bg = bg.to_crs("EPSG:4326")
        backgrounds.append(bg)
    return backgrounds


def plot_map(backgrounds, gdf_lines, output_image):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(20, 20))

    for bg in backgrounds:
        bg.plot(ax=ax, color='#222222', edgecolor='white')

    gdf_lines.plot(ax=ax, color='orange', linewidth=4)

    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()

    # new_ymin = ymin
    new_ymin = ymin + (ymax - ymin) * 0.25

    ax.set_ylim(new_ymin, ymax)
    ax.set_xlim(xmin, xmax)

    ax.set_title('铁路足迹', fontsize=20, color='white')
    ax.axis('off')

    plt.savefig(output_image, dpi=300, bbox_inches='tight')
    print(f"地图已保存为 {output_image}")


def main():
    kml_folder = r"./"   # 设置KML文件路径
    background_files = [r"CHN.json"]   # 设置底图文件路径
    # background_files = [r"background.json",r"background1.json"]
    # 如果程序读取CHN.json失败：请注释第79行，解注释第80行；同时注释第65行，解注释64行
    output_image = "railway_trace_map.png"

    gdf_lines = load_kml_lines(kml_folder)
    if gdf_lines is None:
        return

    backgrounds = load_backgrounds(background_files)
    plot_map(backgrounds, gdf_lines, output_image)


if __name__ == "__main__":
    main()
