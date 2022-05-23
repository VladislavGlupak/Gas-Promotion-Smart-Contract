// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "OpenZeppelin/openzeppelin-contracts@3.0.0//contracts/token/ERC721/ERC721.sol";

contract GasPromo is ERC721 {

    using SafeMath for uint;

    address payable owner = msg.sender;
    uint256 public minGallons;
    bool public stopPromo;
    string public fullTokenName = "Gas Promo Token";
    string public gasToken = "GPT";
    bool public isJoined = false;
    uint256 public nftPrice;

    struct gasNft {
        address ownerNft;
        uint256 nftRate;
    }

    enum GasTypeRate { 
        REGULAR, 
        MIDDLE, 
        PREMIUM }
    
    address[] public clients;
    mapping(address => uint) public balances;
    mapping(GasTypeRate => uint256) public rates;
    mapping(uint256 => gasNft) public nftCollection;

    constructor() ERC721(fullTokenName, gasToken) public {
        minGallons = 5;
        balances[owner] = 10000000;
        stopPromo = false;
        nftPrice = 500;
        rates[GasTypeRate.REGULAR] = 1;
        rates[GasTypeRate.MIDDLE] = 2;
        rates[GasTypeRate.PREMIUM] = 3;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only contract owner can mint tokens!!!");
        _;
    }

    modifier stopPromoFalse() {
        require(stopPromo == false, "Promotion is stopped.");
        _;
    }

    modifier joinedPromo() {
        for (uint256 i = 0; i < clients.length; i++){
                if (msg.sender == clients[i]) {
                    isJoined = true;
                }
        }
        require(isJoined == true, "Please, join the promo!");
        _;
    }

    event boughtGas(address buyer, uint256 amount);
    event genNft(uint256 tokenId, uint256 amount);

    function enterPromo() public stopPromoFalse {
        clients.push(msg.sender);
    }

    function setRate(uint256 rate_gas1, uint256 rate_gas2, uint256 rate_gas3) public {
        rates[GasTypeRate.REGULAR] = rate_gas1;
        rates[GasTypeRate.MIDDLE] = rate_gas2;
        rates[GasTypeRate.PREMIUM] = rate_gas3;
    }

    function changeRate(uint256 newRate, GasTypeRate gas) view public {
        rates[gas] == newRate;
    }

    function getRate(GasTypeRate gas) public view returns (uint256){
        return rates[gas];
    }

    function buyGas(uint256 numberGallons, GasTypeRate gas) public payable stopPromoFalse joinedPromo {

        uint256 amount = numberGallons * rates[gas];

        require(numberGallons >= minGallons, "Promo requires to buy at least 5 gallons!");
        require(amount <= balances[owner], "Sorry! Tokens are out!");

        balances[msg.sender] = balances[msg.sender].add(amount);
        balances[owner] = balances[owner].sub(amount); 

        isJoined = false;  

        emit boughtGas(msg.sender, amount);     
    }

    function getBalance() public view returns (uint) {
        return balances[msg.sender];
    }

    function mint(uint value) public onlyOwner {
        balances[owner] += value;
    }

    function stopPromotion(bool _stopPromo) public onlyOwner returns (bool){
        stopPromo = _stopPromo;

        for (uint256 i = 0; i < clients.length; i++){
            address client = clients[i];
            balances[client] = 0;
        }
        clients = new address[](0);

        return stopPromo;
    }

    function mintNft(string memory tokenURI) public returns (uint256) {
        require(balances[msg.sender] >= nftPrice, "You balance is not enougth for generating NFT!");

        uint256 tokenId = totalSupply();
        address ownerNft = msg.sender;

        balances[ownerNft] = balances[ownerNft].sub(nftPrice);

        _mint(ownerNft, tokenId);
        _setTokenURI(tokenId, tokenURI);

        nftCollection[tokenId] = gasNft(ownerNft, nftPrice);

        emit genNft(tokenId, nftPrice);

        return tokenId;
    }

    function setNftPrice(uint256 _newNftPrice) public {
        nftPrice = _newNftPrice;
    }
}