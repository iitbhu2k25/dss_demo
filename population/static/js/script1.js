let code_to_villagename = {};
let villagePopulations = {};
let chartInstances = {};
document.addEventListener('DOMContentLoaded', () => {
    // Fetch states on page load
    fetch('/population/get-states/')
      .then(response => response.json())
      .then(states => populateDropdown('state', states, 'state_code', 'region_name'))
      .catch(error => console.error('Error fetching states:', error));
  
    // Event listener for state selection
    document.getElementById('state').addEventListener('change', function () {
      const stateCode = this.value;
      if (stateCode) {
        fetch(`/population/get-districts/${stateCode}/`)
          .then(response => response.json())
          .then(districts => populateDropdown('district', districts, 'district_code', 'region_name'))
          .catch(error => console.error('Error fetching districts:', error));
      }
      resetDropdown('district');
      resetDropdown('subdistrict');
      resetTownVillage();
    });
  
    // Event listener for district selection
    document.getElementById('district').addEventListener('change', function () {
      const stateCode = document.getElementById('state').value;
      const districtCode = this.value;
      if (districtCode) {
        fetch(`/population/get-subdistricts/${stateCode}/${districtCode}/`)
          .then(response => response.json())
          .then(subdistricts => populateDropdown('subdistrict', subdistricts, 'subdistrict_code', 'region_name'))
          .catch(error => console.error('Error fetching subdistricts:', error));
      }
      resetDropdown('subdistrict');
      resetTownVillage();
    });
  
    // Event listener for subdistrict selection
    document.getElementById('subdistrict').addEventListener('change', function () {
      const stateCode = document.getElementById('state').value;
      const districtCode = document.getElementById('district').value;
      const subdistrictCode = this.value;
      if (subdistrictCode) {
        fetch(`/population/get-villages/${stateCode}/${districtCode}/${subdistrictCode}/`)
          .then(response => response.json())
          .then(villages => populateTownVillage(villages, 'village_code', 'region_name', 'population_2011'))
          .catch(error => console.error('Error fetching villages:', error));
          
      }
      resetTownVillage();
    });
  });
  
  // Populate dropdown options
  function populateDropdown(dropdownId, data, valueKey, textKey) {
    const dropdown = document.getElementById(dropdownId);
    dropdown.innerHTML = '<option value="">Select an Option</option>';
    data.forEach(item => {
      const option = document.createElement('option');
      option.value = item[valueKey];
      option.textContent = item[textKey];
      dropdown.appendChild(option);
    });
  }
  
  // Reset dropdown options
  function resetDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    dropdown.innerHTML = '<option value="">Select an Option</option>';
  }
  
  // Populate town/village container
  function populateTownVillage(data, valueKey, textKey, populationKey) {
    // console.log("Data hai ", data);
   
    
    const container = document.getElementById('town-village-container');
    container.innerHTML = ''; // Clear previous checkboxes
  
    data.forEach(item => {
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.value = item[valueKey];
      checkbox.id = `village-${item[valueKey]}`;
      checkbox.className = 'village-checkbox';
      villagePopulations[item[valueKey]] = item[populationKey];
      code_to_villagename[item[valueKey]] = item[textKey];
  
      const label = document.createElement('label');
      label.htmlFor = checkbox.id;
      label.textContent = item[textKey];
  
      const div = document.createElement('div');
      div.appendChild(checkbox);
      div.appendChild(label);
  
      container.appendChild(div);
  
      // Add event listener to update selected villages
      checkbox.addEventListener('change', updateSelectedVillages);
    });
  }
  
  // Reset town/village container
  function resetTownVillage() {
    const container = document.getElementById('town-village-container');
    container.innerHTML = '<span>No options available</span>';
    const selectedContainer = document.getElementById('selected-villages');
    selectedContainer.innerHTML = '<span>No selections made</span>';
  }
  
 




  // Update selected villages display
  function updateSelectedVillages() {
    const checkboxes = document.querySelectorAll('.village-checkbox:checked');
    const selectedContainer = document.getElementById('selected-villages');
    const totalPopulationContainer = document.getElementById('total-population');
    let totalPopulation = 0;

    if (checkboxes.length === 0) {
      selectedContainer.innerHTML = '<span>No selections made</span>';
      totalPopulationContainer.innerHTML = '';
      return;
    }

    selectedContainer.innerHTML = '';
    checkboxes.forEach(checkbox => {
      // console.log("Checkbox: ", checkbox); 
      
      
      const label = document.querySelector(`label[for="${checkbox.id}"]`);
      // console.log("Label: ", label);
      
      const div = document.createElement('div');
      const villageId = checkbox.id.split("-")[1]; // Get the village ID from the checkbox ID
      
      // Get the population for the village from the villagePopulations object
      const population = villagePopulations[villageId] || 0; // Default to 0 if not found
      totalPopulation += population; // Add to total population

      // Add the village name and population next to each other
      div.textContent = `${label.textContent} (Population of 2011: ${population})`;
      selectedContainer.appendChild(div);
    });
    totalPopulationContainer.textContent = `Total Population: ${totalPopulation}`;
    
}

  









//   ----------------------calculate and show dynamic table----------------------------

document.addEventListener('DOMContentLoaded', () => {
    const projectionDropdown = document.getElementById('projection-method');
    const projectionItems = document.querySelectorAll('.projection-item');
    const singleYearOption = document.getElementById('single-year-option');
    const rangeYearOption = document.getElementById('range-year-option');
    const targetYearInput = document.getElementById('target-year');
    const targetYearRangeStart = document.getElementById('target-year-range-start');
    const targetYearRangeEnd = document.getElementById('target-year-range-end');
    
    
   
    

    // Handle year selection options
    singleYearOption.addEventListener('change', () => {
      targetYearInput.disabled = false;
      targetYearRangeStart.disabled = true;
      targetYearRangeEnd.disabled = true;
    });

    rangeYearOption.addEventListener('change', () => {
      targetYearInput.disabled = true;
      targetYearRangeStart.disabled = false;
      targetYearRangeEnd.disabled = false;
    });

    // Event listener for projection method dropdown
    projectionDropdown.addEventListener('change', function () {
      const selectedValue = this.value;

      projectionItems.forEach(item => {
        const container = item.querySelector(`#dynamic-tables-${selectedValue}`);
        if (selectedValue === 'all') {
          projectionItems.forEach(item => {
            item.style.display = 'block'; // Show all items
            const methodClass = item.classList[1]; // Get the class corresponding to the method
            const method = methodClass; // Use the class name directly as it matches the dropdown value
            handleProjection(method); // Call handleProjection for each method
          });
          
          
        } else if (item.classList.contains(selectedValue)) {
          item.style.display = 'block';
          if (container) container.innerHTML = ''; // Clear previous tables for this method
        } else {
          item.style.display = 'none';
        }
        
       
      });

      if (selectedValue !== 'all') {
        handleProjection(selectedValue);
      }
      
    });

    // Function to handle projection logic
    function handleProjection(projectionMethod) {
      const state = document.getElementById('state').value;
      const district = document.getElementById('district').value;
      const subdistrict = document.getElementById('subdistrict').value;

      const selectedVillages = Array.from(
        document.querySelectorAll('#town-village-container input[type="checkbox"]:checked')
      ).map(village => village.id);

      const baseYear = document.getElementById('base-year').value;

      const yearSelection = document.querySelector('input[name="year_selection"]:checked')?.value;
      let targetYear = null;
      let targetYearRange = null;

      if (yearSelection === 'single') {
        targetYear = targetYearInput.value;
      } else if (yearSelection === 'range') {
        targetYearRange = {
          start: targetYearRangeStart.value,
          end: targetYearRangeEnd.value,
        };
      }

      // Validate inputs
      if (!state || selectedVillages.length === 0 || !projectionMethod ||
        (!targetYear && (!targetYearRange || !targetYearRange.start || !targetYearRange.end))) {
        alert('Please fill out all required fields.');
        return;
      }


      const requestData = {
        state,
        district,
        subdistrict,
        villages: selectedVillages,
        baseYear,
        projectionMethod,
        targetYear,
        targetYearRange,
        csrfmiddlewaretoken: '{{ csrf_token }}',
      };

      // Fetch data and populate table
      fetch('/population/calculate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      })
        .then(response => response.json())
        .then(data => {
          if (data.success && data.result) {
            console.log("Data Result ", data.result);
            
            populateTable(data.result, projectionMethod);

            // Render graphs for each method
            Object.keys(data.result).forEach(method => {
              const methodData = data.result[method];
              console.log("method ", method);
              console.log("methodData ", methodData);
              
              const canvasId = `graph-${method}`;
              console.log("Canvas Id ", canvasId);
              
              const labels = Object.keys(methodData[Object.keys(methodData)[0]]); // Years
              console.log("Object.keys(methodData)[0] ",Object.keys(methodData)[0]);
              console.log("methodData[Object.keys(methodData)[0]]", methodData[Object.keys(methodData)[0]]);
              

              const datasets = Object.entries(methodData).map(([village, yearData]) => {
                console.log(" Object.values(yearData) ", Object.values(yearData));
                return {
                  label: code_to_villagename[village],
                  data: Object.values(yearData),
                  borderColor: getRandomColor(),
                  borderWidth: 2,
                  fill: false,
                };
              });
              // console.log("datasets ", datasets);
              
              labels.shift()

               // Iterate over each key of the datasets object
              Object.keys(datasets).forEach(key => {
                // Remove the first element from the data array of each dataset
                datasets[key].data.shift();  // or datasets[key].data.splice(0, 1);
              });
          
              renderGraph(canvasId, datasets, labels);
            });

          } else {
            alert('Error: ' + (data.error || 'No data returned'));
          }
        })
        .catch(error => {
          console.error('Fetch error:', error);
          alert('An unexpected error occurred.');
        });
    }

    // Function to populate table
    function populateTable(result, projectionMethod) {
      const containerId = `dynamic-tables-${projectionMethod}`;
      const dynamicTableContainer = document.getElementById(containerId);
  
      // Clear previous tables in the selected container
      dynamicTableContainer.innerHTML = '';
  
      const methodData = result[projectionMethod];
      if (!methodData || Object.keys(methodData).length === 0) {
          console.error("No data available for projection method:", projectionMethod);
          const errorMessage = document.createElement('p');
          errorMessage.textContent = `No data available for ${projectionMethod.replace(/-/g, ' ').toUpperCase()}`;
          dynamicTableContainer.appendChild(errorMessage);
          return;
      }
  
      const tableContainer = document.createElement('div');
      tableContainer.classList.add('mb-5');
  
      const title = document.createElement('h4');
      title.textContent = projectionMethod.replace(/-/g, ' ').toUpperCase();
      tableContainer.appendChild(title);
  
      const tableWrapper = document.createElement('div');
      tableWrapper.style.overflowX = 'auto'; // Allow horizontal scrolling
      tableWrapper.style.maxWidth = '100%'; // Prevent from exceeding container width
  
      const table = document.createElement('table');
      table.classList.add('table', 'table-bordered', 'table-striped');
  
      const thead = document.createElement('thead');
      const headerRow = document.createElement('tr');
      headerRow.innerHTML = '<th>Village/Town Name</th>';
  
      const firstVillageData = Object.values(methodData)[0];
      if (!firstVillageData) {
          console.error("First village data is undefined or null.");
          return;
      }
  
      const firstVillageYears = Object.keys(firstVillageData);
      console.log("firstVillageYears ", firstVillageYears);
  
      firstVillageYears.forEach(year => {
          const th = document.createElement('th');
          th.textContent = year;
          headerRow.appendChild(th);
      });
      thead.appendChild(headerRow);
      table.appendChild(thead);
      console.log("methodData ", methodData);
  
      const tbody = document.createElement('tbody');
      for (const villageCode in methodData) {
          const row = document.createElement('tr');
          const villageCell = document.createElement('td');
          villageCell.textContent = code_to_villagename[villageCode] || "END";
          row.appendChild(villageCell);
  
          const yearData = methodData[villageCode];
          firstVillageYears.forEach(year => {
              const yearCell = document.createElement('td');
              yearCell.textContent = yearData[year] || '-';
              row.appendChild(yearCell);
          });
  
          tbody.appendChild(row);
      }
  
      table.appendChild(tbody);
      tableWrapper.appendChild(table);
      tableContainer.appendChild(tableWrapper);
      dynamicTableContainer.appendChild(tableContainer);
  }
  
    
  });






  // js for showing graph-----------------------------------------------------------------------------------------------------------------------------------------------------------


  document.addEventListener("DOMContentLoaded", () => {
    const projectionMethodDropdown = document.getElementById("projection-method");
    const toggleViewButton = document.getElementById("toggle-view");
    const tablesView = document.querySelector(".tables-view");
    const graphsView = document.querySelector(".graphs-view");
  
    let isGraphView = false;
  
    toggleViewButton.addEventListener("click", (e) => {
      e.preventDefault();
      isGraphView = !isGraphView;
      toggleViewButton.textContent = isGraphView ? "Show Tables" : "Show Graphs";
      tablesView.style.display = isGraphView ? "none" : "block";
      graphsView.style.display = isGraphView ? "block" : "none";
  
      // Update visibility of graphs based on selected method
      updateProjectionView();
    });
  
    projectionMethodDropdown.addEventListener("change", updateProjectionView);
  
    function updateProjectionView() {
      const selectedMethod = projectionMethodDropdown.value;
    
      // Hide all tables and graphs
      document.querySelectorAll(".projection-item").forEach((item) => (item.style.display = "none"));
      document.querySelectorAll(".graph-container").forEach((container) => {
        container.classList.remove("active");
        container.style.display = "none"; // Hide graph containers by default
      });
    
      if (selectedMethod === "all") {
        if (isGraphView) {
          document.querySelectorAll(".graph-container").forEach((container) => {
            container.classList.add("active");
            container.style.display = "block"; // Ensure visibility
          });
        } else {
          document.querySelectorAll(".projection-item").forEach((item) => (item.style.display = "block"));
        }
      } else {
        const specificTable = document.querySelector(`.projection-item.${selectedMethod}`);
        const specificGraphContainer = document.getElementById(`container-${selectedMethod}`);
    
        if (isGraphView) {
          specificGraphContainer.classList.add("active");
          specificGraphContainer.style.display = "block"; // Show selected graph
        } else if (specificTable) {
          specificTable.style.display = "block"; // Show selected table
        }
      }
    }
    
    
  });

  
  // Example renderGraph function call:
  function renderGraph(canvasId, datasets, labels) {
    const canvas = document.getElementById(canvasId);
  
    // Ensure the parent container and canvas are visible
    const container = canvas.parentElement;
    container.style.display = "block";
    container.classList.add("active");
  
    // Resize the canvas to fit its container
    canvas.style.width = "100%";
    canvas.style.height = "350px"; // Set an appropriate height
  
    // Destroy the previous chart instance if it exists
    if (chartInstances[canvasId]) {
      chartInstances[canvasId].destroy();
    }
  
    // Create a new chart instance and store it
    const ctx = canvas.getContext("2d");
    const chart = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: datasets,
      },
      options: {
        responsive: true,
        maintainAspectRatio: false, // Adjust dimensions freely
        plugins: {
          legend: { position: "top" },
        },
        scales: {
          x: { title: { display: true, text: "Years" } },
          y: { title: { display: true, text: "Population" } },
        },
      },
    });
  
    // Save the chart instance for future cleanup
    chartInstances[canvasId] = chart;
  }
    

  
  

  
  function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }
  




// ------------------demographic methods calculation------------------------

document.addEventListener("DOMContentLoaded", function () {
  // Enable/Disable year inputs based on selection
  document.querySelectorAll("input[name='year_selection']").forEach((radio) => {
    radio.addEventListener("change", function () {
      const isRange = this.value === "range";
      document.getElementById("target-year").disabled = isRange;
      document.getElementById("target-year-range-start").disabled = !isRange;
      document.getElementById("target-year-range-end").disabled = !isRange;
    });
  });

  document.getElementById("submit-btn").addEventListener("click", function (e) {
      e.preventDefault();
      const state = document.getElementById('state').value;
      const district = document.getElementById('district').value;
      const subdistrict = document.getElementById('subdistrict').value;
      
      const singleYearOption = document.getElementById('single-year-option');
      const rangeYearOption = document.getElementById('range-year-option');
      const targetYearInput = document.getElementById('target-year');
      const targetYearRangeStart = document.getElementById('target-year-range-start');
      const targetYearRangeEnd = document.getElementById('target-year-range-end');

      const birthRate = document.getElementById("birth-rate").value;
      const deathRate = document.getElementById("death-rate").value;
      const emigrationRate = document.getElementById("emigration-rate").value;
      const immigrationRate = document.getElementById("immigration-rate").value;

      const selectedVillages = Array.from(
        document.querySelectorAll('#town-village-container input[type="checkbox"]:checked')
      ).map(village => village.id);

      const baseYear = document.getElementById('base-year').value;

      const yearSelection = document.querySelector('input[name="year_selection"]:checked')?.value;
      let targetYear = null;
      let targetYearRange = null;


    // Handle year selection options
    singleYearOption.addEventListener('change', () => {
      targetYearInput.disabled = false;
      targetYearRangeStart.disabled = true;
      targetYearRangeEnd.disabled = true;
    });

    rangeYearOption.addEventListener('change', () => {
      targetYearInput.disabled = true;
      targetYearRangeStart.disabled = false;
      targetYearRangeEnd.disabled = false;
    });
    

    if (yearSelection === 'single') {
      targetYear = targetYearInput.value;
    } else if (yearSelection === 'range') {
      targetYearRange = {
        start: targetYearRangeStart.value,
        end: targetYearRangeEnd.value,
      };
    }

    console.log("Birth rate = ", birthRate);
    console.log("Death rate = ", deathRate);
    console.log("emigration rate = ", emigrationRate);
    console.log("immigration rate = ", immigrationRate);
    

    // Validate inputs
    if (!state || selectedVillages.length === 0 || !birthRate || !deathRate || !emigrationRate || !immigrationRate ||
      (!targetYear && (!targetYearRange || !targetYearRange.start || !targetYearRange.end))) {
      alert('Please fill out all required fields.');
      return;
    }

    
    const requestData = {
      state,
      district,
      subdistrict,
      villages : selectedVillages,
      baseYear,
      targetYear,
      targetYearRange,
      birthRate,
      deathRate,
      emigrationRate,
      immigrationRate,
    };

    

    fetch("/population/calculate-demographic/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestData),
    })
      .then(response => response.json())
      .then(data => {
        if(data.success && data.result){
          console.log("result = ", data.result); 
          populateTable(data.result, "demographic-attribute"); 

          Object.keys(data.result).forEach(method => {
            const methodData = data.result[method];
            console.log("method ", method);
            console.log("methodData ", methodData);
            
            const canvasId = `graph-${method}`;
            console.log("Canvas Id ", canvasId);
            
            const labels = Object.keys(methodData[Object.keys(methodData)[0]]); // Years
            console.log("Object.keys(methodData)[0] ",Object.keys(methodData)[0]);
            console.log("methodData[Object.keys(methodData)[0]]", methodData[Object.keys(methodData)[0]]);
            

            const datasets = Object.entries(methodData).map(([village, yearData]) => {
              console.log(" Object.values(yearData) ", Object.values(yearData));
              return {
                label: code_to_villagename[village],
                data: Object.values(yearData),
                borderColor: getRandomColor(),
                borderWidth: 2,
                fill: false,
              };
            });
            console.log("datasets ", datasets);
           
            labels.shift()
            // Iterate over each key of the datasets object
            Object.keys(datasets).forEach(key => {
              // Remove the first element from the data array of each dataset
              datasets[key].data.shift();  // or datasets[key].data.splice(0, 1);
            });

            renderGraph(canvasId, datasets, labels);
          });
        }
        
      })
      .catch(error => console.error("Error:", error));
      
  });

  function populateTable(result, projectionMethod) {

    console.log(code_to_villagename);
    

    const containerId = `dynamic-tables-${projectionMethod}`;
    const dynamicTableContainer = document.getElementById(containerId);
  
    // Clear previous tables in the selected container
    dynamicTableContainer.innerHTML = '';
     
    

    const methodData = result[projectionMethod];
    if (!methodData || Object.keys(methodData).length === 0) {
      console.error("No data available for projection method:", projectionMethod);
      const errorMessage = document.createElement('p');
      errorMessage.textContent = `No data available for ${projectionMethod.replace(/-/g, ' ').toUpperCase()}`;
      dynamicTableContainer.appendChild(errorMessage);
      return;
    }
  
    const tableContainer = document.createElement('div');
    tableContainer.classList.add('mb-5');


   
  
    const title = document.createElement('h4');
    title.textContent = projectionMethod.replace(/-/g, ' ').toUpperCase();
    tableContainer.appendChild(title);
  
    const table = document.createElement('table');
    table.classList.add('table', 'table-bordered', 'table-striped');
  
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    headerRow.innerHTML = '<th>Village/Town Name</th>';
  
    const firstVillageData = Object.values(methodData)[0];
    if (!firstVillageData) {
      console.error("First village data is undefined or null.");
      return;
    }
  
    const firstVillageYears = Object.keys(firstVillageData);
    console.log("firstVillageYears ", firstVillageYears);
    
    firstVillageYears.forEach(year => {
      const th = document.createElement('th');
      th.textContent = year;
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    console.log("methodData ", methodData);
    
    const tbody = document.createElement('tbody');
    for (const villageCode in methodData) {
      const row = document.createElement('tr');
      const villageCell = document.createElement('td');
      villageCell.textContent = code_to_villagename[villageCode] || "END";
      row.appendChild(villageCell);
  
      const yearData = methodData[villageCode];
      firstVillageYears.forEach(year => {
        const yearCell = document.createElement('td');
        yearCell.textContent = yearData[year] || '-';
        row.appendChild(yearCell);
      });
  
      tbody.appendChild(row);
    }
  
    table.appendChild(tbody);
    tableContainer.appendChild(table);
    dynamicTableContainer.appendChild(tableContainer);
  }
  
});





  



      