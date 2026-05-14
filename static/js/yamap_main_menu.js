initMap();

async function initMap() {
    await ymaps3.ready;

    const {YMap, YMapDefaultSchemeLayer, YMapDefaultFeaturesLayer, YMapMarker} = ymaps3;

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

    map.addChild(new YMapDefaultSchemeLayer());
    map.addChild(new YMapDefaultFeaturesLayer());

    function createMarkerElement(ticket) {
        const markerElement = document.createElement('div');
        markerElement.className = 'custom-marker';
        markerElement.style.cursor = 'pointer';

        const imgDiv = document.createElement('div');
        imgDiv.className = 'marker-image';
        imgDiv.style.backgroundImage = 'url("/static/images/point_img.png")';
        imgDiv.style.backgroundSize = 'contain';
        imgDiv.style.backgroundRepeat = 'no-repeat';

        markerElement.appendChild(imgDiv);

        markerElement.onclick = () => {
            const card = document.querySelector('.city-card');

            if (card) {
                card.classList.remove('is-empty');
            }
            document.getElementById('title-for-card').innerText = ticket.title;
            document.getElementById('text-for-card').innerText = ticket.description;

            const imgElement = document.getElementById('img-for-card');
            imgElement.src = ticket.photo
                ? `/static/${ticket.photo}`
                : '/static/images/for_alt_card.png';
        };

        return markerElement;
    }

    try {
        const response = await fetch('/api/v1/markers');
        const tickets = await response.json();

        tickets.forEach(ticket => {

            const newMarker = new YMapMarker({
                coordinates: [parseFloat(ticket.lat), parseFloat(ticket.lon)]
            }, createMarkerElement(ticket));

            map.addChild(newMarker);
        });
    } catch (e) {
        console.error("Ошибка загрузки меток:", e);
    }
}