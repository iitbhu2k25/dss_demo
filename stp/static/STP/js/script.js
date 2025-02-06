async function loadStatesData() {
    const response = await fetch('stp/get_states/');
    statesData = await response.json();
    const stateSelect = document.getElementById('state');
    statesData.forEach(state => {
        const option = new Option();
        console.log(option);
        stateSelect.add(option);
    });
}
