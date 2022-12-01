function getProperty(entity, name) {
    var properties = entity['properties'].split("|");
    for (j = 0; j < properties.length; j++) {
        if (properties[j].includes(`${name}`)) {
            result = properties[j].split("=")[1];
        }
    }
    return result
}