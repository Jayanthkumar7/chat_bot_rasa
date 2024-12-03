
    function increase() {
        let countInput = document.getElementById('count');
        countInput.value = parseInt(countInput.value) + 1;
    }

    function decrease() {
        let countInput = document.getElementById('count');
        if (parseInt(countInput.value) > 0) {
            countInput.value = parseInt(countInput.value) - 1;
        }
    }

