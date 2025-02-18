document.addEventListener('DOMContentLoaded', () => {
    const stateDropdown = document.getElementById('state_dropdown');
    const districtDropdown = document.getElementById('district_dropdown');
    const subdistrictDropdown = document.getElementById('subdistrict_dropdown');
    const calculateButton = document.getElementById('calculate_button');
    const resultContainer = document.getElementById('result_container');
    const villageContainer = document.getElementById('village-container');
    const selectedVillagesContainer = document.getElementById('selected-villages');

    const fetchLocations = (url, dropdown, placeholder) => {
        fetch(url)
            .then(response => response.json())
            .then(locations => {


                locations.sort((a, b) => a.name.localeCompare(b.name));


                dropdown.innerHTML = ''; // Clear existing options
                const defaultOption = document.createElement('option');
                defaultOption.value = '';
                defaultOption.textContent = placeholder;
                dropdown.appendChild(defaultOption);

                locations.forEach(location => {
                    const option = document.createElement('option');
                    option.value = location.code;
                    option.textContent = location.name;
                    dropdown.appendChild(option);
                });
            })
            .catch(error => console.error('Error fetching locations:', error));
    };


    const fetchVillages = (url, container, selectedContainer) => {
        fetch(url)
            .then(response => response.json())
            .then(villages => {
                container.innerHTML = ''; // Clear the container
    
                if (villages.length === 0) {
                    container.innerHTML = '<p class="text-center">No villages available.</p>';
                    return;
                }
    
                // Separate villages with code === 0
                const specialVillage = villages.find(village => village.code === 0);
                const otherVillages = villages.filter(village => village.code !== 0);
    
                // Sort other villages by name in alphabetical order
                otherVillages.sort((a, b) => a.name.localeCompare(b.name));
    
                // Create a function to add a checkbox
                const addCheckbox = (village, displayName) => {
                    const checkboxWrapper = document.createElement('div');
                    checkboxWrapper.classList.add('form-check');
    
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.classList.add('form-check-input');
                    checkbox.id = `village_${village.code}`;
                    checkbox.value = village.code;
                    checkbox.dataset.name = village.name;
    
                    const label = document.createElement('label');
                    label.classList.add('form-check-label');
                    label.htmlFor = `village_${village.code}`;
                    label.textContent = displayName;
    
                    checkbox.addEventListener('change', () => {
                        updateSelectedVillages(selectedContainer);
                    });
    
                    checkboxWrapper.appendChild(checkbox);
                    checkboxWrapper.appendChild(label);
                    return checkboxWrapper;
                };
    
                // Add the special village (code === 0) at the top, with the name "ALL"
                if (specialVillage) {
                    container.appendChild(addCheckbox(specialVillage, ' ALL'));
                }
    
                // Add the remaining villages
                otherVillages.forEach(village => {
                    container.appendChild(addCheckbox(village, village.name));
                });
            })
            .catch(error => console.error('Error fetching villages:', error));
    };
    
    const updateSelectedVillages = (selectedContainer) => {
        const selectedCheckboxes = document.querySelectorAll('#village-container input[type="checkbox"]:checked');
        const selectedVillages = Array.from(selectedCheckboxes).map(checkbox => ({
            code: checkbox.value,        // for sending to the backend
            name: checkbox.dataset.name    // for display purposes
        }));

        selectedContainer.innerHTML = selectedVillages.length
            ? selectedVillages.map(village => `<span class="badge bg-primary me-1">${village.name}</span>`).join('')
            : '<p class="text-muted">No villages selected.</p>';
    };
    


    fetchLocations('waterdemand/get_locations/', stateDropdown, 'Select State');

    stateDropdown.addEventListener('change', () => {
        const stateCode = stateDropdown.value;
        fetchLocations(`waterdemand/get_locations/?state_code=${stateCode}`, districtDropdown, 'Select District');
    });

    districtDropdown.addEventListener('change', () => {
        const stateCode = stateDropdown.value;
        const districtCode = districtDropdown.value;
        fetchLocations(`waterdemand/get_locations/?state_code=${stateCode}&district_code=${districtCode}`, subdistrictDropdown, 'Select Subdistrict');
    });

    subdistrictDropdown.addEventListener('change', () => {
        const stateCode = stateDropdown.value;
        const districtCode = districtDropdown.value;
        const subdistrictCode = subdistrictDropdown.value;

        if (subdistrictCode) {
            const url = `waterdemand/get_locations/?state_code=${stateCode}&district_code=${districtCode}&subdistrict_code=${subdistrictCode}`;
            fetchVillages(url, villageContainer, selectedVillagesContainer);
        }
    });
    calculateButton.addEventListener('click', () => {
        resultContainer.innerHTML = ''; // Clear previous results
        
        const surfaceWater = parseFloat(document.getElementById('surface_water').value) || 0;
        const directGroundwater = parseFloat(document.getElementById('direct_groundwater').value) || 0;
        const numTubewells = parseFloat(document.getElementById('num_tubewells').value) || 0;
        const dischargeRate = parseFloat(document.getElementById('discharge_rate').value) || 0;
        const operatingHours = parseFloat(document.getElementById('operating_hours').value) || 0;
        
        const groundwaterCalc = numTubewells * dischargeRate * operatingHours;
        
        if (directGroundwater > 0 && (numTubewells > 0 || dischargeRate > 0 || operatingHours > 0)) {
            resultContainer.innerHTML = '<h4 class="text-danger">Error: Provide either direct groundwater supply or calculated groundwater supply, not both.</h4>';
            return;
        }
        
        
        const groundwaterSupply = directGroundwater > 0 ? directGroundwater : groundwaterCalc;

        const directAlternate = parseFloat(document.getElementById('direct_alternate').value) || 0;
        const rooftopTank = parseFloat(document.getElementById('rooftop_tank').value) || 0;
        const aquiferRecharge = parseFloat(document.getElementById('aquifer_recharge').value) || 0;
        const surfaceRunoff = parseFloat(document.getElementById('surface_runoff').value) || 0;
        const reuseWater = parseFloat(document.getElementById('reuse_water').value) || 0;
        
        const alternateCalc = rooftopTank + aquiferRecharge + surfaceRunoff + reuseWater;
        
        if (directAlternate > 0 && (rooftopTank > 0 || aquiferRecharge > 0 || surfaceRunoff > 0 || reuseWater > 0)) {
            resultContainer.innerHTML = '<h4 class="text-danger">Error: Provide either direct alternate water supply or calculated alternate water supply, not both.</h4>';
            return;
        }
        
        const alternateWaterSupply = directAlternate > 0 ? directAlternate : alternateCalc;

        const totalWaterSupply = surfaceWater + groundwaterSupply + alternateWaterSupply;
        resultContainer.innerHTML = `<h4>Total Water Supply for Selected Region is: ${totalWaterSupply.toFixed(2)} MLD</h4>`;
    });

});