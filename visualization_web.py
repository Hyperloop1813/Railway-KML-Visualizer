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

def create_base_map():
    m = folium.Map(location=[35, 105], zoom_start=4, tiles=None)
    folium.TileLayer('CartoDB positron', name='Positron').add_to(m)
    folium.TileLayer('CartoDB Voyager', name='Voyager').add_to(m)
    folium.TileLayer('cartodb dark_matter', name='Dark_matter').add_to(m)
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
    return m



def create_feature_groups():
    return {
        'red': folium.FeatureGroup(name='红色线路'),
        'green': folium.FeatureGroup(name='绿色线路'),
        'blue': folium.FeatureGroup(name='蓝色线路'),
        'purple': folium.FeatureGroup(name='紫色线路'),
        'black': folium.FeatureGroup(name='黑色线路'),
        'white': folium.FeatureGroup(name='白色线路'),
        'orange': folium.FeatureGroup(name='橙色线路'),
    }


def add_line_to_groups(line, file_name, groups, weight=4):
    color_map = {
        'red': '#FF0000',
        'green': '#3CB371',
        'blue': '#1E90FF',
        'purple': '#FF00FF',
        'black': '#000000',
        'white': '#FFFFFF',
        'orange': '#FFA500',
    }

    for group_name, group in groups.items():
        # 透明背景线（用于宽度调节）
        folium.PolyLine(line, color='black', weight=15, opacity=0, tooltip=file_name,
                        class_name="transparent-line").add_to(group)
        # 实际彩色线
        folium.PolyLine(line, color=color_map[group_name], weight=weight, opacity=1, tooltip=file_name,
                        class_name="real-line").add_to(group)


def add_slider_control(map_object):
    html = """
        <div style="position: absolute; bottom: 20px; right: 20px; z-index: 9999; background-color: white; padding: 10px; border-radius: 5px;">
            <label for="line-width-slider" style="font-size: 14px;">调整线路宽度:</label>
            <input type="range" id="line-width-slider" min="2" max="8" value="4" step="1" style="width: 200px;">
            <span id="line-width-value" style="font-size: 14px;">4</span> px
        </div>
        """
    map_object.get_root().html.add_child(folium.Element(html))

    js_script = """
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
        """
    map_object.get_root().html.add_child(folium.Element(js_script))


def main():
    kml_folder = r"./"  # 设置KML文件夹路径
    output_html = "railway_trace_map.html"

    kml_files = [os.path.join(kml_folder, f) for f in os.listdir(kml_folder) if f.lower().endswith('.kml')]
    all_lines = []
    kml_line_map = {}

    for kml_file in kml_files:
        lines = extract_lines_from_kml_simple(kml_file)
        if lines:
            all_lines.extend(lines)
            kml_line_map[kml_file] = lines

    if not all_lines:
        print("没有解析到任何线路，程序终止。")
        return

    m = create_base_map()
    groups = create_feature_groups()

    for group in groups.values():
        group.add_to(m)

    for kml_file, lines in kml_line_map.items():
        file_name = clean_filename(os.path.basename(kml_file))
        for line in lines:
            add_line_to_groups(line, file_name, groups)

    add_slider_control(m)
    folium.LayerControl().add_to(m)
    m.save(output_html)
    print(f"HTML 地图已保存为 {output_html}")


if __name__ == "__main__":
    main()