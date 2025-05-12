function loadKajron() {
    const b92Checked = document.getElementById("b92").checked;
    const n1Checked = document.getElementById("n1").checked;
    const danasChecked = document.getElementById("danas").checked;
    const sites = [];

    if (b92Checked) sites.push("B92");
    if (n1Checked) sites.push("N1");
    if (danasChecked) sites.push("Danas");

    fetch("/get_news", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ sites: sites })
    })
    .then(response => response.json())
    .then(data => {
        const kajronText = document.getElementById("kajron-text");
        if (data.length > 0) {
            kajronText.innerText = data.join(" | ");
        } else {
            kajronText.innerText = "Nema dostupnih vesti.";
        }
        restartAnimation(b92Checked, n1Checked, danasChecked);
    });
}

function restartAnimation(b92Checked, n1Checked, danasChecked) {
    const kajronText = document.getElementById("kajron-text");
    kajronText.style.animation = "none";
    void kajronText.offsetWidth;

    const brojIzabranih = [b92Checked, n1Checked, danasChecked].filter(Boolean).length;

    if (brojIzabranih === 1) {
        kajronText.style.animation = "scroll-left 500s linear infinite";
    } else if (brojIzabranih === 2) {
        kajronText.style.animation = "scroll-left 300s linear infinite";
    } else {
        kajronText.style.animation = "scroll-left 200s linear infinite";
    }
}

window.onload = loadKajron;
