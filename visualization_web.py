import os
from lxml import etree
import folium
from folium import plugins

def extract_lines_from_kml_simple(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = etree.parse(f)

    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    coords_elements = tree.xpath('//kml:LineString/kml:coordinates', namespaces=ns)

    lines = []
    for elem in coords_elements:
        coord_text = elem.text.strip()
        coord_pairs = coord_text.split()
        coords = [(float(c.split(',')[1]), float(c.split(',')[0])) for c in coord_pairs if ',' in c]
        if len(coords) >= 2:
            lines.append(coords)
    print(f"从 {os.path.basename(file_path)} 提取 LineString 数: {len(lines)}")
    return lines


def clean_filename(name):
    left = name.find('(')
    right = name.find(')', left)
    if left != -1 and right != -1:
        name = name[:left] + name[right + 1:]
    return name.replace('.kml', '')


def main():
    kml_folder = r"./"  # 更换自己的KML文件路径
    output_html = "railway_trace_map.html"

    kml_files = [os.path.join(kml_folder, f) for f in os.listdir(kml_folder) if f.lower().endswith('.kml')]

    all_lines = []
    for kml_file in kml_files:
        lines = extract_lines_from_kml_simple(kml_file)
        all_lines.extend(lines)

    if not all_lines:
        print("没有解析到任何线路，程序终止。")
        return

    m = folium.Map(location=[35, 105], zoom_start=4, tiles=None)

    folium.TileLayer('CartoDB positron', name='Positron').add_to(m)
    folium.TileLayer('CartoDB Voyager', name='Voyager').add_to(m)
    folium.TileLayer('cartodb dark_matter', name='Dark_matter').add_to(m)
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)


    red_group = folium.FeatureGroup(name='红色线路').add_to(m)
    green_group = folium.FeatureGroup(name='绿色线路').add_to(m)
    blue_group = folium.FeatureGroup(name='蓝色线路').add_to(m)
    purple_group = folium.FeatureGroup(name='紫色线路').add_to(m)
    black_group = folium.FeatureGroup(name='黑色线路').add_to(m)
    white_group = folium.FeatureGroup(name='白色线路').add_to(m)
    orange_group = folium.FeatureGroup(name='橙色线路').add_to(m)

    line_weight = 4

    html = """
        <div style="position: absolute; bottom: 20px; right: 20px; z-index: 9999; background-color: white; padding: 10px; border-radius: 5px;">
            <label for="line-width-slider" style="font-size: 14px;">调整线路宽度:</label>
            <input type="range" id="line-width-slider" min="2" max="8" value="4" step="1" style="width: 200px;">
            <span id="line-width-value" style="font-size: 14px;">4</span> px
        </div>
        """
    m.get_root().html.add_child(folium.Element(html))


    m.get_root().html.add_child(folium.Element("""
        <script>
            const slider = document.getElementById('line-width-slider');
            const valueDisplay = document.getElementById('line-width-value');

            slider.oninput = function() {
                valueDisplay.textContent = slider.value;
                updateLineWidth(slider.value);
            }

            function updateLineWidth(weight) {
                const transparentLines = document.querySelectorAll('.transparent-line');
                transparentLines.forEach(line => {
                    line.setAttribute('stroke-width', 15);
                });

                const realLines = document.querySelectorAll('.real-line');
                realLines.forEach(line => {
                    line.setAttribute('stroke-width', weight);
                });
            }
        </script>
        """))

    for kml_file in kml_files:
        file_name = clean_filename(os.path.basename(kml_file))
        lines = extract_lines_from_kml_simple(kml_file)

        for line in lines:

            folium.PolyLine(line, color='black', weight=15, opacity=0, tooltip=file_name, class_name="transparent-line").add_to(orange_group)
            folium.PolyLine(line, color='black', weight=15, opacity=0, tooltip=file_name, class_name="transparent-line").add_to(red_group)
            folium.PolyLine(line, color='black', weight=15, opacity=0, tooltip=file_name, class_name="transparent-line").add_to(green_group)
            folium.PolyLine(line, color='black', weight=15, opacity=0, tooltip=file_name, class_name="transparent-line").add_to(blue_group)
            folium.PolyLine(line, color='black', weight=15, opacity=0, tooltip=file_name, class_name="transparent-line").add_to(purple_group)
            folium.PolyLine(line, color='black', weight=15, opacity=0, tooltip=file_name, class_name="transparent-line").add_to(white_group)
            folium.PolyLine(line, color='black', weight=15, opacity=0, tooltip=file_name, class_name="transparent-line").add_to(black_group)

            folium.PolyLine(line, color='#FFA500', weight=4, opacity=1, tooltip=file_name,
                            class_name="real-line").add_to(orange_group)  # 橙色
            folium.PolyLine(line, color='#FF0000', weight=4, opacity=1, tooltip=file_name,
                            class_name="real-line").add_to(red_group)  # 红色
            folium.PolyLine(line, color='#1E90FF', weight=4, opacity=1, tooltip=file_name,
                            class_name="real-line").add_to(blue_group)  # 蓝色
            folium.PolyLine(line, color='#3CB371', weight=4, opacity=1, tooltip=file_name,
                            class_name="real-line").add_to(green_group)  # 绿色
            folium.PolyLine(line, color='#000000', weight=4, opacity=1, tooltip=file_name,
                            class_name="real-line").add_to(black_group)  # 黑色
            folium.PolyLine(line, color='#FFFFFF', weight=4, opacity=1, tooltip=file_name,
                            class_name="real-line").add_to(white_group)  # 白色
            folium.PolyLine(line, color='#FF00FF', weight=4, opacity=1, tooltip=file_name,
                            class_name="real-line").add_to(purple_group)  # 紫色

    folium.LayerControl().add_to(m)

    m.save(output_html)
    print(f"HTML 地图已保存为 {output_html}")


if __name__ == "__main__":
    main()
