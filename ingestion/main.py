from fetch import fetch_html


def main():

    html = fetch_html()

    print(type(html))

    print(len(html))


if __name__ == "__main__":
    main()