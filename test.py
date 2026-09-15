import requests
from bs4 import BeautifulSoup


def parse_points(html):
    """Parse the document table into a coordinate-to-character mapping."""
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table tr")[1:]

    points = {}
    for row in rows:
        cells = row.select("td")
        if len(cells) != 3:
            continue

        x = int(cells[0].get_text(strip=True))
        character = cells[1].get_text(strip=True)
        y = int(cells[2].get_text(strip=True))

        points[(x, y)] = character

    return points


def render_grid(points):
    """Render coordinate data as a printable character grid."""
    if not points:
        return ""

    max_x = max(x for x, _ in points)
    max_y = max(y for _, y in points)

    return "\n".join(
        "".join(points.get((x, y), " ") for x in range(max_x + 1))
        for y in range(max_y, -1, -1)
    )


def decode_secret_message(url):
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    points = parse_points(response.text)
    print(render_grid(points))


if __name__ == "__main__":
    url = "https://docs.google.com/document/d/e/2PACX-1vSvM5gDlNvt7npYHhp_XfsJvuntUhq184By5xO_pA4b_gCWeXb6dM6ZxwN8rE6S4ghUsCj2VKR21oEP/pub"
    decode_secret_message(url)