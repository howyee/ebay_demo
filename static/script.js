async function loadListings() {

  const response = await fetch("/api/listings");

  const listings = await response.json();

  console.log(listings);

  const container = document.getElementById("listings");

  container.innerHTML = "";

  listings.forEach(item => {

    const card = document.createElement("div");
    card.className = "card";

    card.innerHTML = `
      <div class="image-section">

        <img
          class="main-image"
          src="${item.images?.[0] || ''}"
        />

        <div class="thumbnail-row">

          ${(item.images || []).map(image => `

            <img
              class="thumbnail"
              src="${image}"
            />

          `).join('')}

        </div>

      </div>

      <div class="card-content">

        <h2>${item.title || 'No Title'}</h2>

        <p>
          ${item.description || ''}
        </p>

        <p class="price">
          ${item.price || 'N/A'}
          ${item.currency || ''}
        </p>

        <p>
          Quantity:
          ${item.quantity || 0}
        </p>

        <p>
          Brand:
          ${item.brand || 'N/A'}
        </p>

        <p>
          Condition:
          ${item.condition || 'N/A'}
        </p>

        <p>
          SKU:
          ${item.sku || ''}
        </p>

      </div>
    `;

    container.appendChild(card);

    // =========================
    // THUMBNAIL CLICK
    // =========================

    const mainImage = card.querySelector(".main-image");

    const thumbnails = card.querySelectorAll(".thumbnail");

    thumbnails.forEach(thumbnail => {
      thumbnail.addEventListener("click", () => {
        mainImage.src = thumbnail.src;
      });
    });

  });

}

loadListings();