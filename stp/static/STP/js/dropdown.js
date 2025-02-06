document.addEventListener('DOMContentLoaded', async () => {
    // Console log to verify script loading
    console.log('Script loaded');
    
    try {
        const response = await fetch('/STP/get_states/');
        console.log('Fetching states:', response);
        const data = await response.json();
        populateStates(data.states);
    } catch (error) {
        console.error('Error:', error);
    }
});

function populateStates(states) {
    const stateSelects = [1,2,3,4].map(i => document.getElementById(`state${i}`));
    const defaultOption = '<option value="">Select State</option>';
    stateSelects.forEach(select => {
        select.innerHTML = defaultOption + states.map(state =>
            `<option value="${state.id}">${state.name}</option>`
        ).join('');
    });
}

// Rest of your existing functions...