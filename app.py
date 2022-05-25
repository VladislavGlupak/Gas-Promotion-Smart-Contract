import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from pathlib import Path

from infura import send_to_ipfs
from random_pic import generateImage

load_dotenv()

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

################################################################################
# Contract Helper function:

################################################################################


@st.cache(allow_output_mutation=True)
def load_contract():

    # Load the contract ABI
    with open(Path('./contracts/compiled/compiled.json')) as f:
        contract_abi = json.load(f)

    # Set the contract address (this is the address of the deployed contract)
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=contract_abi
    )

    return contract

    # Load the contract
contract = load_contract()

################################################################################

################################################################################

with st.sidebar:
    st.image("./Pictures/gas_st.gif")
    st.write("Choose an account to get started")
    accounts = w3.eth.accounts
    owner = w3.eth.accounts[0]
    address = st.selectbox("Select Account", options=accounts)
    st.markdown("---")
    st.markdown("# Admin panel")

    total = contract.functions.balances(owner).call()
    if st.button("Check owner balance"):
        st.write(f"### Balance of the tokens: {total}")

    st.markdown("### Mint tokens")
    number_of_tokens = int(st.number_input('', min_value=0, max_value=None, value=1000000, step=500))
    if st.button("Mint"):
        contract.functions.mint(number_of_tokens).transact({
        "from": address,
        "gas": 1000000
        })
        st.markdown("### Done!")
    st.markdown("---")

    st.markdown("### Set rewards")
    rate1 = int(st.number_input('Reg', min_value=0, max_value=10, value=1, step=1))
    rate2 = int(st.number_input('Mid', min_value=0, max_value=10, value=2, step=1))
    rate3 = int(st.number_input('Pre', min_value=0, max_value=10, value=3, step=1))
    if st.button("Set rewards rate"):
        contract.functions.setRate(rate1, rate2, rate3).transact({
        "from": address,
        "gas": 1000000
        })
        st.markdown("### Done!")
    st.markdown("---")

    st.markdown("### Set NFT exchange rate")
    nft_rate = int(st.number_input('Reg', min_value=0, max_value=None, value=500, step=5))
    if st.button("Set NFT price"):
        contract.functions.setNftPrice(nft_rate).transact({
        "from": address,
        "gas": 1000000
        })
        st.markdown("### Done!")
    if st.button("Current rate"):
        cur_nft_rate = contract.functions.nftPrice().call()
        st.write(f"### Current exchange rate: {cur_nft_rate}")
    st.markdown("---")

    st.markdown("### Stop/Start promotion")
    nft_rate = st.checkbox("Checked = stop / Unchecked = start", value=False)
    if st.button("Stop/Start"):
        contract.functions.stopPromotion(nft_rate).transact({
        "from": address,
        "gas": 1000000
        })
        st.markdown("### Done!")

st.image("./Pictures/main.jpg")
st.markdown("---")
st.markdown("### Do you want to join the promo?")
if st.button("Join", key=0):
    contract.functions.enterPromo().transact({
        "from": address,
        "gas": 1000000
    })

    st.markdown("#### Great! You are now a member of the promotion!")
st.markdown("---")

st.markdown("### Do you want to buy some gas?")
gas_choice = st.radio("What's your favorite gas?", ('Regular', 'Middle', 'Premium'))
if gas_choice == "Regular":
    gas_code = 0
if gas_choice == "Middle":
    gas_code = 1
if gas_choice == "Premium":
    gas_code = 2
number = int(st.number_input('Insert a number of gallons', min_value=0, max_value=None, value=5, step=1))


token_name = contract.functions.symbol().call()
if st.button("My balance"):
    balance = contract.functions.balances(address).call()
    st.write(f"{balance} {token_name} tokens")
nft_price = contract.functions.nftPrice().call()
if st.button("Buy", key=1):
    contract.functions.buyGas(number, gas_code).transact({
        "from": address,
        "gas": 1000000
    })
    balance = contract.functions.balances(address).call()
    st.markdown("#### Tokens have been minted!")
    st.write(f"You have collected tokens: {balance}.")
    if (balance >= nft_price):
        st.write(f"You can exchange them for NFT!")
st.markdown("---")


st.markdown("### Create NFT")

if st.button("Get it!"):
    balance = contract.functions.balances(address).call()
    if (balance >= nft_price):
        with st.spinner("Spill some oil... Don't worry nature is safe :)"):
            file = generateImage()
            st.image(file)

        hash = send_to_ipfs(file)

        artwork_uri = f"https://infura-ipfs.io/ipfs/{hash}"

        tx_hash = contract.functions.mintNft(artwork_uri).transact({
            "from": address,
            "gas": 1000000
        })
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write("Here is your link:")
        st.write(artwork_uri)
        st.write("")
        st.write("Transaction receipt mined:")
        a = dict(receipt)
        #st.write(dict(receipt))
        st.write(a["transactionHash"])
    else:
        st.write("You don't have enougth token balance!")

st.markdown("---")

if st.button("See my NFTs"):
    contract.functions.getNftUri().transact({
            "from": address,
            "gas": 1000000
        })

    nft_list = contract.functions.getUri().call()
    for link in nft_list:
        st.write(link)

st.markdown("---")