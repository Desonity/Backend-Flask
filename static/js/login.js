/*responsible for user login*/

const spendingLimit = {
    "GlobalDESOLimit": 1 * 1e9, // 1 DESO
    TransactionCountLimitMap: {
        AUTHORIZE_DERIVED_KEY: 2,
        BASIC_TRANSFER: 5,
        SUBMIT_POST: 5
    },
    CreatorCoinOperationLimitMap: {
        "": {
            "any": 5,
            "buy": 5,
            "sell": 5,
            "transfer": 5
        }
    },
    DAOCoinOperationLimitMap: {
        "": {
            "any": 5,
            "mint": 5,
            "burn": 5,
            "transfer": 5,
            "update_transfer_restriction_status": 5,
            "disable_minting": 5
        }
    },
    NFTOperationLimitMap: {
        "": {
            0: {
                "any": 5
            }
        }
    }

};

function login(derive) {
    if (derive) {
        identityWindow = window.open(
            "https://identity.deso.org/derive?transactionSpendingLimitResponse=" + encodeURIComponent(JSON.stringify(spendingLimit)),
            null,
            "toolbar=no, width=800, height=1000, top=0, left=0"
        );
    } else {
        identityWindow = window.open(
            "https://identity.deso.org/log-in?accessLevelRequest=2",
            null,
            "toolbar=no, width=800, height=1000, top=0, left=0"
        );
    }
}

// function logout() {
//     axios.post("/logout")
//         .then(() => { window.location.reload() })
//         .catch((e) => { console.log(e) });
// }

function handleInit(e) {
    if (!init) {
        init = true;
        iframe = document.getElementById("identity");

        for (const e of pendingRequests) {
            postMessage(e);
        }

        pendingRequests = [];
    }
    respond(e.source, e.data.id, {});
}

function handleLogin(payload) {
    // console.log(payload);
    if (identityWindow) {
        identityWindow.close();
        identityWindow = null;
    }
    if (payload.publicKeyAdded) {
        console.log("got the key " + payload.publicKeyAdded);
        axios.post("/setKey", { "publicKey": payload.publicKeyAdded })
            .catch((e) => { console.log(e) })
            .then((res) => { if (res.data === "OK") window.location.replace('/success'); else alert("unable to perform action") });
    }
    // if (payload.signedTransactionHex) {
    //     console.log("transaction signed " + payload.signedTransactionHex);
    //     axios.post("/submit-txn", { "TransactionHex": payload.signedTransactionHex })
    //         .then((res) => { console.log("transaction submitted " + res.data); alert("Transaction successfull") });
    // }
}

function handleDerive(payload) {
    if (identityWindow) {
        identityWindow.close();
        identityWindow = null;
    }
    console.log(payload);

    if (payload.derivedPublicKeyBase58Check) {
        console.log("got the key " + payload.derivedPublicKeyBase58Check);
        axios.post("/setKey", {
            "derivedKey": payload.derivedPublicKeyBase58Check,
            "derivedSeedHex": payload.derivedSeedHex,
            "publicKey": payload.publicKeyBase58Check,
            "expirationBlock": payload.expirationBlock,
            "accessSignature": payload.accessSignature,
            "transactionSpendingLimitHex": payload.transactionSpendingLimitHex,
        })
            .catch((e) => { console.log(e) })
            .then((res) => { if (res.data === "OK") window.location.replace('/success'); else alert("unable to perform action") });

    }

}


function respond(e, t, n) {
    e.postMessage(
        {
            id: t,
            service: "identity",
            payload: n,
        },
        "*"
    );
}

function postMessage(e) {
    init
        ? this.iframe.contentWindow.postMessage(e, "*")
        : pendingRequests.push(e);
}

// const childWindow = document.getElementById('identity').contentWindow;
window.addEventListener("message", (message) => {
    // console.log("message: ");
    // console.log(message);

    const {
        data: { id: id, method: method, payload: payload },
    } = message;

    // console.log(id);
    // console.log(method);
    // console.log(payload);

    if (method == "initialize") {
        handleInit(message);
    } else if (method == "login") {
        handleLogin(payload);
    } else if (method == "derive") {
        handleDerive(payload);
    }
});

var init = false;
var iframe = null;
var pendingRequests = [];
var identityWindow = null;
