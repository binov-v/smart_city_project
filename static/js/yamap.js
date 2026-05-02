initMap();
        async function initMap() {
            await ymaps3.ready;

            const {YMap, YMapDefaultSchemeLayer, YMapDefaultFeaturesLayer, YMapMarker, YMapListener} = ymaps3;

            const map = new YMap(
                document.getElementById('map'),
                {
                    location: {
                        center: [39.8917, 59.2205],
                        zoom: 12
                    },
                    restrictMapArea: [[39.7500, 59.1500], [40.0500, 59.3000]],
                    zoomRange: {min: 12, max: 100}
                }
            );
            const schemeLayer = new YMapDefaultSchemeLayer();
            map.addChild(schemeLayer);

            const markersLayer = new YMapDefaultFeaturesLayer();
            map.addChild(markersLayer);

            function createMarkerElement() {
                const markerElement = document.createElement('div');
                markerElement.className = 'custom-marker';

                const imgDiv = document.createElement('div');
                imgDiv.className = 'marker-image';
                imgDiv.style.backgroundImage = 'url("../static/images/point_img.png")';
                imgDiv.style.backgroundSize = 'contain';
                imgDiv.style.backgroundRepeat = 'no-repeat';

                markerElement.appendChild(imgDiv);

                const title = document.createElement('span');
                title.innerText = 'Я здесь';
                title.style.cssText = 'position:absolute; bottom: -20px; left: 50%; transform: translateX(-50%); font-weight: bold; white-space: nowrap;';
                markerElement.appendChild(title);

                return markerElement;
            }

            const clickListener = new YMapListener({
            layer: 'any',
            onClick: (object, event) => {
                if (object) {
                    const lon = object.entity.coordinates[0];
                    const lat = object.entity.coordinates[1];
                    const aboutMarker = document.createElement('div');
                    console.log(lon)
                    console.log(lat)
                    aboutMarker.innerHTML = `<h1>Очень классная метка. Координаты: ${lon.toFixed(5)}, ${lat.toFixed(5)}</h1>`;
                    document.body.appendChild(aboutMarker);
                    return;
                    }
                const coords = event.coordinates;

                const newMarker = new YMapMarker(
                    { coordinates: coords, draggable: true },
                    createMarkerElement()
                );

                map.addChild(newMarker);
            }
        });

            map.addChild(clickListener);
        }