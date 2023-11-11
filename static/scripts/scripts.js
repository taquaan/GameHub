console.log("GameID from Flask:", GameID);
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

        gameTitle.textContent = data[0].game_title;
        gameDescription.innerHTML = data[0].description;
        gameUpdateLogs.innerHTML = data[0].update_logs;
        gamePublisher.textContent = data[0].publisher;
        gameDeveloper.textContent = data[0].developer;
        gameReleaseDate.textContent = data[0].release_date;

        console.log(data[0].update_logs);

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
        let allRecommendedNull = true;

        for (const key in sys_req) {
            if (pattern.test(key)) {
                //  Populate the System Requirements section
                const value = sys_req[key];
                const divID = key;
                const divElement = document.getElementById(divID);
                if (divElement) {
                    // Set the content of the div with the value
                    divElement.innerHTML = value;
                    if (value !== null) {
                        allRecommendedNull = false;
                    }
                }
                if (value === null && divElement.parentElement) {
                    divElement.parentElement.classList.add("hidden");}

                //  Check if Recommended section is null
                    if (allRecommendedNull === true) {
                        const windowsDiv = document.getElementById("Windows");
                        if (windowsDiv) {
                        // Within the "Windows" div, select the div with the ID "Recommended"
                            const recommendedSection = windowsDiv.querySelector('#Recommended');
                                if (recommendedSection) {
                                recommendedSection.classList.add("hidden");
                            }
                        }
                        const macOSDiv = document.getElementById("macOS");
                        if (macOSDiv) {
                            // Within the "macOS" div, select the div with the ID "Recommended"
                            const recommendedSection = macOSDiv.querySelector('#Recommended');
                            if (recommendedSection) {
                            recommendedSection.classList.add("hidden");
                            }
                        }
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

                copyrightElements.innerHTML = data[1].Copyright;
                languageAudioElements.textContent = data[1].LanguageAudio;
                languageTextElements.textContent = data[1].LanguageText;
            }
        }
    })

