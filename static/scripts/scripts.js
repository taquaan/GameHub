console.log("GameID from Flask:", GameID);


// Generate stars based on score
function generateStarRating(score) {
    const containers = document.getElementsByClassName('rating-container');

    for (let i = 0; i < containers.length; i++) {
        const container = containers[i];
        const totalStars = 5;
        const filledStars = Math.floor(score);
        const hasHalfStar = score % 1 >= 0.5;

        // Add filled stars
        for (let n = 0; n < filledStars; n++) {
            const star = document.createElement('i');
            star.className = 'fa-solid fa-star-sharp';
            container.appendChild(star);
        }

        // Add half-filled star if needed
        if (hasHalfStar) {
            const halfStar = document.createElement('i');
            halfStar.className = 'fa-regular fa-star-sharp-half-stroke';
            container.appendChild(halfStar);
        }

        // Add outline stars to fill the container (adjust as needed)
        const remainingStars = totalStars - filledStars - (hasHalfStar ? 1 : 0);
        for (let n = 0; n < remainingStars; n++) {
            const outlineStar = document.createElement('i');
            outlineStar.className = 'fa-regular fa-star-sharp';
            container.appendChild(outlineStar);
        }
    }
}


/// Make a request to the API endpoint
fetch(`/api/${GameID}`)
    .then(response => response.json())
    .then(data => {

        // Populate the HTML elements with the retrieved data
        const gameTitle = document.getElementById("game-title-placeholder");
        const gameDescription = document.getElementById("game-desc-placeholder");
        const gameUpdateLogs = document.getElementById("update-logs-placeholder");
        const gamePublisher = document.getElementById("publisher-placeholder");
        const gameDeveloper = document.getElementById("developer-placeholder");
        const gameReleaseDate = document.getElementById("release-date-placeholder");
        const gameSupportedOS = document.getElementById("supported-os");
        const gameReviewText = document.getElementsByClassName("overall-review-placeholder");
        const gameReviewScore = document.getElementById("score-placeholder");

        gameTitle.textContent = data[0].game_title;
        gameDescription.innerHTML = data[0].description;
        gameUpdateLogs.innerHTML = data[0].update_logs;
        gamePublisher.textContent = data[0].publisher;
        gameDeveloper.textContent = data[0].developer;
        gameReleaseDate.textContent = data[0].release_date;
        gameReviewScore.textContent = data[0].review_score;
        generateStarRating(data[0].review_score);

        for (var i = 0; i < gameReviewText.length; i++) {
            gameReviewText[i].textContent = data[0].review_text;
            const reviewcolor = gameReviewText[1];
            if (data[0].review_text.endsWith("Positive")) {
                reviewcolor.parentElement.style.color="#00FF0A80"
                reviewcolor.parentElement.style.backgroundcolor="#00FF0A20"
            }
            if (data[0].review_text.endsWith("Mixed")) {
                reviewcolor.parentElement.style.color="#ffb70080"
                reviewcolor.parentElement.style.backgroundColor="#ffb70020"
            }
            if (data[0].review_text.endsWith("Negative")) {
                reviewcolor.parentElement.style.color="#ff1e1e80"
                reviewcolor.parentElement.style.backgroundColor="#ff1e1e20"
            }
        }

        const tagsList = data[0].tags.split(', '); // Assuming data[0].tags contains the tag string
        const tagContainer = document.getElementById("tagsContainer");
        
        for (let i = 0; i < tagsList.length; i++) {
            const tag = tagsList[i].trim(); // Trim to remove leading/trailing whitespaces
        
            // Create a new p element for each tag
            const tagElement = document.createElement("p");
            tagElement.textContent = tag;
        
            // Append the new p element to the tagContainer
            tagContainer.appendChild(tagElement);
        }

        if (gameSupportedOS) {
            const winicon = gameSupportedOS.querySelector('#supported-os-win');
            const macicon = gameSupportedOS.querySelector('#supported-os-mac');
            const linuxicon = gameSupportedOS.querySelector('#supported-os-linux');
            if (!data[0].supported_os.includes("Windows")) {
                winicon.classList.add("hidden");
            }
            if (!data[0].supported_os.includes("macOS")) {
                macicon.classList.add("hidden");
            }
            if (!data[0].supported_os.includes("Linux")) {
                linuxicon.classList.add("hidden");
            }
        }

        if (data[0].update_logs === null) {
            // If the value is null, hide the section using CSS
            gameUpdateLogs.parentElement.classList.add('hidden');
        }



        var discountPer = data[0].discount;
        var oldPrice = data[0].old_price;
        var newPrice = data[0].new_price;
        var inapp = data[0].in_app;
    
        // Get the discount-per container and specific div elements
        var discountPerContainer = document.getElementById("discount-per-container");
        var specificDiv = discountPerContainer.nextElementSibling;
    
        // Check if discountPer is greater than 0
        if (discountPer > 0) {
          // Format discountPer to display as a percentage with a minus sign
          var formattedDiscount = (-discountPer * 100).toFixed(0) + "%";
    
          // Update the discount-per container
          discountPerContainer.textContent = formattedDiscount;
    
          // Update the old price, new price, and footnote
          specificDiv.querySelector(".old-price").textContent = oldPrice;
          specificDiv.querySelector(".new-price").textContent = newPrice;
          if (inapp === "Yes") {specificDiv.querySelector(".footnote").textContent = "Includes in-app purchases";}
        } else {
          // If discountPer is 0, hide the discount-per container
          discountPerContainer.style.display = "none";
          specificDiv.querySelector(".old-price").style.display = "none";
    
          // Update only the new price and footnote
          specificDiv.querySelector(".new-price").textContent = newPrice;
          if (inapp === "Yes") {specificDiv.querySelector(".footnote").textContent = "Includes in-app purchases";}
        }

        //Only for game specifications section
        const sys_req = data[1];
        const pattern = /^((Min|Rec)[A-Za-z]+)(Win|Mac|Linux)$/;

        let allRecommendedNullWin = true;
        let allRecommendedNullMac = true;
        let allRecommendedNullLinux = true;

        for (const key in sys_req) {
            if (pattern.test(key)) {
                //  Populate the System Requirements section
                const value = sys_req[key];
                const divID = key;
                const divElement = document.getElementById(divID);
                if (divElement) {
                    // Set the content of the div with the value
                    divElement.innerHTML = value;
                    // Recommendation Check
                    var startsWithRec = key.startsWith("Rec");
                    var endsWithWin = key.endsWith("Win");
                    var endsWithMac = key.endsWith("Mac");
                    var endsWithLinux = key.endsWith("Linux");
                    if (startsWithRec && endsWithWin) {
                        if (value !== null) {
                            allRecommendedNullWin = false;
                        }
                    }
                    if (startsWithRec && endsWithMac) {
                        if (value !== null) {
                            allRecommendedNullMac = false;
                        }
                    }
                    if (startsWithRec && endsWithLinux) {
                        if (value !== null) {
                            allRecommendedNullLinux = false;
                        }
                    }
                }

                if (value === null && divElement.parentElement) {
                    divElement.parentElement.classList.add("hidden");}
            }
        
        }

        //  Check if Recommended section is null
        if (allRecommendedNullWin === true) {
            const windowsDiv = document.getElementById("Windows");
            if (windowsDiv) {
            // Within the "Windows" div, select the div with the ID "Recommended"
            const recommendedSection = windowsDiv.querySelector('#Recommended');
                if (recommendedSection) {
                    recommendedSection.classList.add("hidden");
                }
            }
        }
        if (allRecommendedNullMac === true) {
            const macOSDiv = document.getElementById("macOS");
            if (macOSDiv) {
            // Within the "macOS" div, select the div with the ID "Recommended"
            const recommendedSection = macOSDiv.querySelector('#Recommended');
                if (recommendedSection) {
                    recommendedSection.classList.add("hidden");
                }
            }
        }
        if (allRecommendedNullLinux === true) {
            const LinuxDiv = document.getElementById("Linux");
            if (LinuxDiv) {
            // Within the "Linux" div, select the div with the ID "Recommended"
            const recommendedSection = LinuxDiv.querySelector('#Recommended');
                if (recommendedSection) {
                    recommendedSection.classList.add("hidden");
                }
            }
        }
            
        //  System Requirements Tabs
        if (!data[0].supported_os.includes("Windows")){
            const windows = document.getElementById("supported-os-win");
            windows.parentElement.classList.add("hidden");
        }
        if (!data[0].supported_os.includes("macOS")){
            const macos = document.getElementById("supported-os-mac");
            macos.parentElement.classList.add("hidden");
        }
        if (!data[0].supported_os.includes("Linux")){
            const linux = document.getElementById("supported-os-linux");
            linux.parentElement.classList.add("hidden");
        }

        //  Other specifications
        const copyrightElements = document.getElementById("copyright-placeholder");
        const languageAudioElements = document.getElementById("audio-placeholder");
        const languageTextElements = document.getElementById("text-placeholder");
        const Bit64Required = document.getElementsByClassName("64-bit-required");

        copyrightElements.innerHTML = data[1].Copyright;
        languageAudioElements.textContent = data[1].LanguageAudio;
        languageTextElements.textContent = data[1].LanguageText;
        for (let i = 0; i < Bit64Required.length; i++) {
            if (data[1].Bit64Required === null){
                Bit64Required[i].parentElement.classList.add("hidden");
            }
        }

        // Features
        const featuresList = ['Singleplayer', 'Multiplayer', 'Online Co-Op', 'Online PvP', 'Controller', 'Achievements', 'Cloud Saves'];
        const featuresArray = data[0].features.split(', ');

        for (let i = 0; i < featuresArray.length; i++) {
            const feature = featuresArray[i].trim(); // Trim to remove leading/trailing whitespaces
            // Check if the feature is in the featuresList
            if (featuresList.includes(feature)) {
                const featuretab = document.getElementById(feature);
                featuretab.style.display = "flex";
            }
        }

        if (data[0].feature_notice != null) {
            const noticeElements = document.getElementById("feature-notice-placeholder");
            noticeElements.innerHTML = data[0].feature_notice;
            noticeElements.parentElement.style.display = "flex";
        }

        const esrbContainer = document.getElementById("esrbContainer");

        if (data[0].esrb !== null && data[0].esrb !== "Not Rated") {
            // Create ESRB Icon
            const esrbIcon = document.createElement("div");
            esrbIcon.className = "esrb-icon";
            const esrbIconImg = document.createElement("img");
            if (data[0].esrb == "Everyone"){esrbIconImg.src = "./static/img/esrb/E.svg";}
            if (data[0].esrb == "Everyone 10+"){esrbIconImg.src = "./static/img/esrb/E10plus.svg";}
            if (data[0].esrb == "Adults Only"){esrbIconImg.src = "./static/img/esrb/AO.svg";}
            if (data[0].esrb == "Mature"){esrbIconImg.src = "./static/img/esrb/M.svg";}
            if (data[0].esrb == "Rating Pending"){esrbIconImg.src = "./static/img/esrb/RP.svg";}
            if (data[0].esrb == "Rating Pending - Likely Mature 17+"){esrbIconImg.src = "./static/img/esrb/RP-LM17.svg";}
            if (data[0].esrb == "Teens"){esrbIconImg.src = "./static/img/esrb/T.svg";}
            esrbIconImg.alt = "ESRB Rating";
            esrbIcon.appendChild(esrbIconImg);

            // Create ESRB Content
            const esrbContentDiv = document.createElement("div");
            esrbContentDiv.className = "esrb-content";

            // Create Rating (e.g., Everyone)
            const ratingHeader = document.createElement("b");
            ratingHeader.textContent = data[0].esrb;
            esrbContentDiv.appendChild(ratingHeader);

            // Create Descriptors
            const descriptorParagraph = document.createElement("p");
            descriptorParagraph.textContent = data[0].esrb_content;
            esrbContentDiv.appendChild(descriptorParagraph);

            // Create Divider
            if (data[0].esrb_interact != null) {
                const divider = document.createElement("div");
                divider.className = "divider";
                esrbContentDiv.appendChild(divider);
            }

            // Create Interactionss
            const interactionsParagraph = document.createElement("p");
            interactionsParagraph.textContent = data[0].esrb_interact;
            esrbContentDiv.appendChild(interactionsParagraph);
            
            // Append everything to the esrbContainer
            esrbContainer.appendChild(esrbIcon);
            esrbContainer.appendChild(esrbContentDiv);
        }
    }
    )

