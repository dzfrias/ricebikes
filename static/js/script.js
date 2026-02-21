const transactionsElem = document.getElementById("transactions-body")

async function updateTransactions(tbody) {
    const response = await fetch("/api/transactions")
    const transactions = await response.json()
    console.log(transactions)
}

updateTransactions(transactionsElem)
