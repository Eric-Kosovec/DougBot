
def parse_spec(type_list, text, separator=' '):
    # Lazy parsing
    chunks = text.split(separator)
    parsed = []

    # TODO COMPLEX STRING STUFF
    # TODO E.G., str int will eat strings until int
    # TODO str at end will take rest as string

    optional = False
    i = 0
    for spec_type in type_list:
        if i not in range(len(chunks)):
            break

        # Next type will be an optional one
        if spec_type == '?':
            optional = True
            continue

        try:
            casted = spec_type(chunks[i])
            parsed.append(casted)
        except ValueError:
            if not optional:
                return None
        finally:
            if not optional:
                i += 1
            optional = False

    return parsed


if __name__ == '__main__':
    print(parse_spec([int, '?', int, str], '1 test'))
