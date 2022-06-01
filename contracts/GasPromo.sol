// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;
pragma experimental ABIEncoderV2;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v3.0.0/contracts/token/ERC721/ERC721.sol";

// This is a contract which represents promotion "Buy gas - get rewards (token GPT) and unique NFT"
contract GasPromo is ERC721 {
    // in order to avoid Math issues, contract uses OpenZeppelin SafeMath contract
    using SafeMath for uint;

    // define variables
    address payable owner = msg.sender;
    uint256 public minGallons;
    bool public stopPromo;
    string public fullTokenName = "Gas Promo Token";
    string public gasToken = "GPT"; // Gas Promo Token - short name
    bool public isJoined = false;
    bool public alreadyJoined = false;
    uint256 public nftPrice;
    string[] public uris;
    uint256[] public points;

    // define struct of needed information for future NFT
    struct gasNft {
        address ownerNft;
        uint256 nftRate;
    }
    // define types of the gas
    enum GasTypeRate { 
        REGULAR, 
        MIDDLE, 
        PREMIUM }
    

    address[] public clients; // array for tracking clients and for resetting balances when stopping promotion
    mapping(address => uint) public balances; // maping for tracking balances
    mapping(GasTypeRate => uint256) public rates; // mapping for tracking rewards exchange rates
    mapping(uint256 => mapping(address => string)) public nftCollection; // mapping for tracking NFTs

    // initialize default values for several variables when contracts deployed
    constructor() ERC721(fullTokenName, gasToken) public {
        minGallons = 5;             // min number gallosfor buying
        balances[owner] = 10000000; // initial token balance for minting
        stopPromo = false;          // promo is on
        nftPrice = 500;             // price of NFT in reward points
        rates[GasTypeRate.REGULAR] = 1;
        rates[GasTypeRate.MIDDLE] = 2;
        rates[GasTypeRate.PREMIUM] = 3;
    }

    // only owner of the contract
    modifier onlyOwner() {
        require(msg.sender == owner, "Only contract owner can perform that procedure!!!");
        _;
    }

    // checking that promotion is still running
    modifier stopPromoFalse() {
        require(stopPromo == false, "Promotion is stopped.");
        _;
    }

    // checking that client joined the promotion (checking clients array)
    modifier joinedPromo() {
        for (uint256 i = 0; i < clients.length; i++){
                if (msg.sender == clients[i]) {
                    isJoined = true;
                }
        }
        require(isJoined == true, "Please, join the promo!");
        _;
    }

        modifier isNewClient() {
        for (uint256 i = 0; i < clients.length; i++){
                if (msg.sender == clients[i]) {
                    alreadyJoined = true;
                }
        }
        require(alreadyJoined == false, "You are already registered!");
        _;
    }

    // define events forlogging buying the gas and creating NFT
    event boughtGas(address buyer, uint256 amount); // gas
    event genNft(uint256 tokenId, uint256 amount);  // NFT

    // define fuction for joining the promotion
    function enterPromo() public stopPromoFalse isNewClient {
        require(msg.sender != owner, "Only clients can enter the promo!");
        clients.push(msg.sender);
    }

    // define function for changing exchange rate gas=>rewards
    function setRate(uint256 rate_gas1, uint256 rate_gas2, uint256 rate_gas3) public {
        rates[GasTypeRate.REGULAR] = rate_gas1;
        rates[GasTypeRate.MIDDLE] = rate_gas2;
        rates[GasTypeRate.PREMIUM] = rate_gas3;
    }

    // define function for checking exchange rate gas=>rewards
    // need to provide number "gas": 0-regular, 1-middle, 2-premium
    function getRate(GasTypeRate gas) public view returns (uint256){
        return rates[gas];
    }

    // define funcdtion for buying gas
    function buyGas(uint256 numberGallons, GasTypeRate gas) public payable stopPromoFalse joinedPromo {

        uint256 amount = numberGallons * rates[gas]; // amount of rewards

        require(numberGallons >= minGallons, "Promo requires to buy at least 5 gallons!"); // min 5 gallong
        require(amount <= balances[owner], "Sorry! Points are out!"); // checking that points are still available

        balances[msg.sender] = balances[msg.sender].add(amount); // update client balance
        balances[owner] = balances[owner].sub(amount); // update owner balance

        isJoined = false; // update to make possible check next client

        emit boughtGas(msg.sender, amount); // register the event    
    }

    // define function for minting additional points
    function mint(uint value) public onlyOwner stopPromoFalse {
        balances[owner] += value;
    }

    // contract owner is able to stop promotion (false => true)
    function stopPromotion(bool _stopPromo) public onlyOwner returns (bool){
        stopPromo = _stopPromo;

        // reset client's balances
        for (uint256 i = 0; i < clients.length; i++){
            address client = clients[i];
            balances[client] = 0;
        }
        balances[owner] = 0;
        clients = new address[](0); // resetting clients array

        return stopPromo; // true
    }

    // minting NFT
    function mintNft(string memory tokenURI) public joinedPromo returns (uint256) {
        require(balances[msg.sender] >= nftPrice, "You balance is not enougth for generating NFT!");

        uint256 tokenId = totalSupply();
        address ownerNft = msg.sender;

        balances[ownerNft] = balances[ownerNft].sub(nftPrice); // update client balance

        _mint(ownerNft, tokenId); // tokenID to msg.sender
        _setTokenURI(tokenId, tokenURI); // assing tokenURI to tokenId

        nftCollection[tokenId][msg.sender] = tokenURI;
        points.push(tokenId); //
        emit genNft(tokenId, nftPrice); // register the event

        return tokenId;
    }

    // define function for changing NFT exchange rate (500 when contract initialized)
    function setNftPrice(uint256 _newNftPrice) public onlyOwner {
        nftPrice = _newNftPrice;
    }

    // perform search of the address => nft and save results to the uris array
    function createNftUriList() public {
        delete uris; // we neeed to reset array before each search
        for (uint256 i = 0; i < points.length; i++){
            uint256 t = points[i];
            address client = msg.sender;
                if ((keccak256(abi.encodePacked(nftCollection[t][client]))) != (keccak256(abi.encodePacked('')))) {
                    uris.push(nftCollection[t][client]);
                }    
        }
    }

    // get array of nfts
    function getUriList() public view returns (string[] memory){
        return uris;
    }
    
    // donate to ...
    function donate(uint256 amount, address donator) public payable {
        require(amount <= balances[donator], "Please, check your balance!");
        address payable receiver = 0x6EF43f60F7ea71681f16E90dF4b180deC1D5d359; // dummy address
        balances[donator] = balances[donator].sub(amount);
        receiver.transfer(msg.value);
    }
}