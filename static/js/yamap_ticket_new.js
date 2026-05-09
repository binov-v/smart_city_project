initMap();

async function initMap() {
    await ymaps3.ready;

    const { YMap, YMapDefaultSchemeLayer, YMapDefaultFeaturesLayer, YMapMarker, YMapListener } = ymaps3;

    const map = new YMap(document.getElementById('map'), {
        location: {
            center: [39.8917, 59.2205],
            zoom: 12
        },
        restrictMapArea: [[39.7500, 59.1500], [40.0500, 59.3000]],
        zoomRange: { min: 12, max: 100 }
    });

    map.addChild(new YMapDefaultSchemeLayer());
    map.addChild(new YMapDefaultFeaturesLayer());

    let marks_list = [];

    function createMarkerElement() {
        const markerElement = document.createElement('div');
        markerElement.className = 'custom-marker';

        const imgDiv = document.createElement('div');
        imgDiv.className = 'marker-image';
        imgDiv.style.backgroundImage = 'url("/static/images/point_img.png")';
        imgDiv.style.backgroundSize = 'contain';
        imgDiv.style.backgroundRepeat = 'no-repeat';

        markerElement.appendChild(imgDiv);

        const title = document.createElement('span');
        title.innerText = 'Тут';
        title.style.cssText = 'position:absolute; bottom:-20px; left:50%; transform:translateX(-50%); font-weight:bold; white-space:nowrap;';
        markerElement.appendChild(title);

        return markerElement;
    }

    const clickListener = new YMapListener({
        layer: 'any',
        onClick: (object, event) => {
            if (object) return;

            if (marks_list.length >= 1) {
                const oldMarker = marks_list.pop();
                map.removeChild(oldMarker);
            }

            const coords = event.coordinates;
            const newMarker = new YMapMarker(
                { coordinates: coords, draggable: false },
                createMarkerElement()
            );
            const coordsInput = document.getElementById('coords');
            if (coordsInput) {
                coordsInput.value = JSON.stringify(coords);
            }

            marks_list.push(newMarker);
            map.addChild(newMarker);
        }
    });

    map.addChild(clickListener);
}