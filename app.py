import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from pathlib import Path

from infura import send_to_ipfs
from random_pic import generateImage

# load veriables from the .env
load_dotenv()

################################################################################
# Define and connect a new Web3 provider
################################################################################

w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

# we need to use st.cache for keep contract in the cache
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
# Administrator panel
# 1. List of accounts
################################################################################

with st.sidebar:
    st.image("./Pictures/gas_st.gif") # load design picture
    st.write("Choose an account to get started")
    accounts = w3.eth.accounts # retrive accounts from the blockchain
    owner = w3.eth.accounts[0] # contract owner 0 in the list
    address = st.selectbox("Select Account", options=accounts)
    st.markdown("---")

################################################################################
# Administrator panel
# 2. Mint tokens
################################################################################

    st.markdown("# Admin panel")

    total = contract.functions.balances(owner).call() # contract owner balance
    # define button for displaying the contract owner's balance
    if st.button("Check owner balance"):
        st.write(f"### Balance of the tokens: {total}")

    st.markdown("### Mint bonus points")
    number_of_tokens = int(st.number_input('', min_value=0, max_value=None, value=1000000, step=500)) # number of tokens to mint
    # define button for minting new tokens
    if st.button("Mint"):
        contract.functions.mint(number_of_tokens).transact({"from": address, "gas": 1000000})
        st.markdown("### Done!")
    st.markdown("---")

################################################################################
# Administrator panel
# 3. Set rewards exchange rate
################################################################################

    st.markdown("### Set exchange rate")
    # set rewards rate for gas types
    rate1 = int(st.number_input('Reg', min_value=0, max_value=10, value=1, step=1))
    rate2 = int(st.number_input('Mid', min_value=0, max_value=10, value=2, step=1))
    rate3 = int(st.number_input('Pre', min_value=0, max_value=10, value=3, step=1))

    # button - set rewards
    if st.button("Set rates"):
        contract.functions.setRate(rate1, rate2, rate3).transact({"from": address, "gas": 1000000})
        st.markdown("### Done!")

    # checking current rewards rate
    rate_check_code = st.selectbox('Check current rate', ('Regular', 'Middle', 'Premium'))
    if rate_check_code == "Regular":
        code = 0
    if rate_check_code == "Middle":
        code = 1
    if rate_check_code == "Premium":
        code = 2
    if st.button("Current exchange rate"):
        check_rate_result = contract.functions.getRate(code).call()
        st.write(check_rate_result)
    st.markdown("---")

################################################################################
# Administrator panel
# 4. Set NFT exchange rate
################################################################################

    st.markdown("### Set NFT exchange rate")
    # define new rate for NFT
    nft_rate = int(st.number_input('Reg', min_value=0, max_value=None, value=500, step=5))
    # set new NFT price
    if st.button("Set NFT price"):
        contract.functions.setNftPrice(nft_rate).transact({"from": address, "gas": 1000000})
        st.markdown("### Done!")
    # retrive current NFT rate
    if st.button("Current rate"):
        cur_nft_rate = contract.functions.nftPrice().call()
        st.write(f"### Current exchange rate: {cur_nft_rate}")
    st.markdown("---")

################################################################################
# Administrator panel
# 5. Stop / Start promotion
################################################################################

    st.markdown("### Stop/Start promotion")
    nft_rate = st.checkbox("Checked = stop / Unchecked = start", value=False)
    # stop/start promotion (True is stop, False is running)
    if st.button("Stop/Start"):
        contract.functions.stopPromotion(nft_rate).transact({"from": address, "gas": 1000000})
        st.markdown("### Done!")
    # get current promotion state
    if st.button("Current state"):
        state = contract.functions.stopPromo().call()
        st.markdown(f"Promotion is stopped: {state}")

################################################################################
# Customer panel
# 1. Join promotion
################################################################################

st.image("./Pictures/main.jpg")
st.markdown("---")
st.markdown("### Do you want to join the promo?")
# customer have to join the promotion
if st.button("Join", key=0):
    contract.functions.enterPromo().transact({"from": address, "gas": 1000000})

    st.markdown("#### Great! You are now a member of the promotion!")
st.markdown("---")

################################################################################
# Customer panel
# 2. Buy gas
################################################################################

st.markdown("### Do you want to buy some gas?")
gas_choice = st.radio("What's your favorite gas?", ('Regular', 'Middle', 'Premium'))
# based on customer's choice, we get exchange rate from the mapping
if gas_choice == "Regular":
    gas_code = 0
if gas_choice == "Middle":
    gas_code = 1
if gas_choice == "Premium":
    gas_code = 2
number = int(st.number_input('Insert a number of gallons', min_value=0, max_value=None, value=5, step=1))

# retrive customer's balance
if st.button("My balance"):
    balance = contract.functions.balances(address).call()
    st.write(f"You balance is {balance} bonus points")
nft_price = contract.functions.nftPrice().call()
# buy gas
if st.button("Buy", key=1):
    contract.functions.buyGas(number, gas_code).transact({"from": address, "gas": 1000000})
    balance = contract.functions.balances(address).call()
    st.markdown("#### Bonus points have been minted!")
    st.write(f"You have collected points: {balance}.")
    # check if customer is allowed to get NFT
    if (balance >= nft_price):
        st.write(f"You can exchange them for NFT!")
st.markdown("---")

################################################################################
# Customer panel
# 3. Donate
################################################################################

st.markdown("### Do you want to donate your bonus points?")
st.image("./Pictures/donate.png")
donate_amount = int(st.number_input('How much do you want to donate?', min_value=0, max_value=None, value=50, step=1))
if st.button("Donate"):
    tx_hash_ = contract.functions.donate(donate_amount, address).transact({
        "from": owner, 
        "value": w3.toWei((donate_amount/(10**5)), "ether"), # we send wei from owner(bank)
        "gas": 1000000})
    st.write("Done! Thank you!")
    receipt_ = w3.eth.waitForTransactionReceipt(tx_hash_)
    st.write("")
    st.write("Transaction receipt mined:")
    st.write(dict(receipt_))
st.markdown("---")

################################################################################
# Customer panel
# 4. Get NFT
################################################################################

st.markdown("### Paint NFT")

if st.button("Start!"):
    # retrive balance of the customer
    balance = contract.functions.balances(address).call()
    if (balance >= nft_price):
        with st.spinner("Spill some oil... Don't worry nature is safe :)"):
            file = generateImage() # call image generation script from random_pic.py
            st.image(file)

        hash = send_to_ipfs(file) # call Infura API

        oil_spot = f"https://infura-ipfs.io/ipfs/{hash}"

        tx_hash = contract.functions.mintNft(oil_spot).transact({"from": address, "gas": 1000000})
        receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        st.write("Here is your link:")
        st.write(oil_spot) # print oil spot link
        st.write("")
        st.write("Transaction receipt mined:")
        #a = dict(receipt)
        st.write(dict(receipt))
        #st.write(a["transactionHash"])
        os.remove(file)
    else:
        st.write("You don't have enougth token balance!")
st.markdown("---")

################################################################################
# Customer panel
# 5. Retrive customer's NFT
################################################################################

st.markdown("### Check my NFT collection")
if st.button("See my NFTs"):
    contract.functions.createNftUriList().transact({"from": address, "gas": 1000000})

    nft_list = contract.functions.getUriList().call()
    if (len(nft_list) == 0):
        st.write("You do not have NFT!")
    else:
        for link in nft_list:
            st.write(link)
st.markdown("---")