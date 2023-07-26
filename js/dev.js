fetch(`../output/perimeter_list.json`)
    .then(response => response.json())
    .then(data => {
        console.log(data);
        data.forEach(element => {
            // console.log(element);
            const layer_name_array = element.split("\\");
            const splitter = layer_name_array[layer_name_array.length - 1];
            const layer_title = splitter.split(".")[0];
            console.log(layer_title);
        });
    })

