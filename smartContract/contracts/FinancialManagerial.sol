// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./Token.sol";

contract FinancialManagerial {

    /// @dev Variabile where store address of society's ERC20
    Token private immutable token;

    /// @dev mapping where store the cost centers of every users
    mapping(address => string[]) public usersCostCenters;

    /// @dev mapping where store the percentage of every cost centers of every users
    mapping(address => mapping(string => uint)) public usersPercentageCostCenters;

    /// @dev mapping where store the amount of token deployed by user in every single cost center of every users
    mapping(address => mapping(string => uint)) public usersStorageArea;

    /// @dev mapping for memorize if a cost center is delete or not
    mapping(address => mapping(string => bool)) public usersCostCentersExist;

    modifier checkUser {
        require(msg.sender != address(0), "User invalid.");
        _;
    }
    
    /// @dev event to emit when user withdraw some tokens
    event WithdrawTokens(address indexed user, uint indexed amount, string costCenter, uint balanceResidual);
    
    /// @dev event to emit when user allocate new tokens
    event DeployNewTokens(address indexed user, uint indexed amount, uint finalBalance);
    
    constructor(Token _address) {
        token = Token(_address);
    }
    
    /// @notice function for inizialize a default cost centers.
    function createDefaultDistribution() external checkUser {
        string[] memory costCenters = usersCostCenters[msg.sender];
        if(costCenters.length != 0) {
            for(uint i=0; i<costCenters.length; ++i) {
                if(usersStorageArea[msg.sender][costCenters[i]] != 0) {
                    revert("Before replace your cost centers, you must withdraw all tokens.");
                }
                delete usersPercentageCostCenters[msg.sender][costCenters[i]];
                delete usersStorageArea[msg.sender][costCenters[i]];
                delete usersCostCentersExist[msg.sender][costCenters[i]];
            }
        }
        usersPercentageCostCenters[msg.sender]["home"] = 50;
        usersPercentageCostCenters[msg.sender]["study"] = 5;
        usersPercentageCostCenters[msg.sender]["investment"] = 15;
        usersPercentageCostCenters[msg.sender]["sport"] = 5;
        usersPercentageCostCenters[msg.sender]["other"] = 25;
        usersCostCenters[msg.sender] = ["home", "study", "investment", "sport", "other"];
        for(uint i=0; i<usersCostCenters[msg.sender].length; ++i) {
            usersStorageArea[msg.sender][usersCostCenters[msg.sender][i]] = 0;
            usersCostCentersExist[msg.sender][usersCostCenters[msg.sender][i]] = true;
        }
    }
    
    /// @notice function for create own cost centers
    function setDistribution(string[] memory _costCenters, uint[] memory _percentages) public checkUser {
        require(_costCenters.length == _percentages.length, "Incompatible data.");
        uint totalPercentage;
        for(uint i=0; i<_percentages.length; ++i) {
            totalPercentage += _percentages[i];
        }
        require(totalPercentage == 100, "The percentage must be equal to 100%.");
        // if users's cost centers already exist
        if(usersCostCenters[msg.sender].length > 0) {
            // before create new cost centers I delete old cost centers; the function revert if there are someone to delete with amount
            // of tokens stored
            bool deleteCostCenter;
            for(uint i=0; i<usersCostCenters[msg.sender].length; ++i) {
                deleteCostCenter = true;
                for(uint y=0; y<_costCenters.length; ++y) {
                    // if a cost center already exist then I don't delete it
                    if(keccak256(abi.encodePacked(usersCostCenters[msg.sender][i])) == keccak256(abi.encodePacked(_costCenters[y]))) {
                        deleteCostCenter = false;
                    }
                }
                // if a cost center is to delete
                if(deleteCostCenter) {
                    // check if a cost center stored some tokens
                    // if there aren't tokens stored then I'm going to delete it
                    if(usersStorageArea[msg.sender][usersCostCenters[msg.sender][i]] == 0) {
                        delete usersPercentageCostCenters[msg.sender][usersCostCenters[msg.sender][i]];
                        delete usersStorageArea[msg.sender][usersCostCenters[msg.sender][i]];
                        delete usersCostCentersExist[msg.sender][usersCostCenters[msg.sender][i]];
                    // if the cost center stored some tokens then I revert
                    } else {
                        revert("Before changing the distribution of your money, you must remove the cost centers that you aren't going to use.");
                    }
                }
            }
        }
        // create new distribution
        for(uint i=0; i<_costCenters.length; ++i) {
            // save the percentage to allocate tokens into the cost centers when it will be deployed
            usersPercentageCostCenters[msg.sender][_costCenters[i]] = _percentages[i];
            usersCostCentersExist[msg.sender][_costCenters[i]] = true;
        }
        // at the end I save the user's cost centers
        usersCostCenters[msg.sender] = _costCenters;
    }

    /// @notice function for delete specific cost center
    function removeCostCenter(string memory _costCenter) external checkUser {
        require(token.balanceOf(address(this)) >= 0, "You didn't deploy enough tokens.");
        require(usersCostCentersExist[msg.sender][_costCenter], "Cost center doesn't exist.");
        uint amountStored = usersStorageArea[msg.sender][_costCenter];
        delete usersPercentageCostCenters[msg.sender][_costCenter];
        delete usersStorageArea[msg.sender][_costCenter];
        delete usersCostCentersExist[msg.sender][_costCenter];
        // modify the usersCostCenters array without the cost center to remove
        string memory lastElement = usersCostCenters[msg.sender][usersCostCenters[msg.sender].length-1];
        for(uint i=0; i<usersCostCenters[msg.sender].length; ++i) {
            if(keccak256(abi.encodePacked(usersCostCenters[msg.sender][i])) == keccak256(abi.encodePacked(_costCenter))) {
                usersCostCenters[msg.sender][i] = lastElement;
            }
        }
        usersCostCenters[msg.sender].pop();
        token.transfer(msg.sender, amountStored);
        emit WithdrawTokens(tx.origin, amountStored, _costCenter, 0);
        assert(usersPercentageCostCenters[msg.sender][_costCenter] == 0 && usersStorageArea[msg.sender][_costCenter] == 0);
    }

    /// @notice function for withdraw specific amount of token
    function withdraw(string memory _costCenter, uint _amount) external checkUser {
        require(usersCostCentersExist[msg.sender][_costCenter], "Cost center doesn't exist.");
        require(_amount != 0, "Amount fo tokens to withdraw uncorrected.");
        require(_amount <= usersStorageArea[msg.sender][_costCenter], "You didn't have enough tokens.");
        require(token.balanceOf(address(this)) >= _amount, "You didn't deploy enough tokens.");
        usersStorageArea[msg.sender][_costCenter] -= _amount;
        token.transfer(msg.sender, _amount);
        uint residualCostCenter = usersStorageArea[msg.sender][_costCenter];
        emit WithdrawTokens(msg.sender, _amount, _costCenter, residualCostCenter);
    }

    /// @notice function for deploy new tokens in your cost centers based on percentage of cost centers
    function deploy(uint _totalAmount) external checkUser {
        if(usersCostCenters[msg.sender].length == 0) {
            revert("Before deploy token you must create a distribution of your cost centers.");
        }
        // variables for distribuite the token of every cost center in based of cost centers percentage
        uint sumAmountCalcolated;
        uint amountCalcolated;
        for(uint i=0; i<usersCostCenters[msg.sender].length; ++i) {
            amountCalcolated  = _totalAmount*usersPercentageCostCenters[msg.sender][usersCostCenters[msg.sender][i]]/100;
            usersStorageArea[msg.sender][usersCostCenters[msg.sender][i]] += amountCalcolated;
            sumAmountCalcolated += amountCalcolated;
        }
        // I check if the total tokens were allocate
        if(sumAmountCalcolated < _totalAmount) {
            usersStorageArea[msg.sender][usersCostCenters[msg.sender][0]] += _totalAmount - sumAmountCalcolated;
        }
        uint balance = totalDeployed();
        emit DeployNewTokens(msg.sender, _totalAmount, balance);
    }

    /// @notice function for know your total cost centers
    function getUserCostCenter() external view returns(string[] memory) {
        return usersCostCenters[msg.sender];
    }

    /// @notice function for know your total token deployed
    /// @dev I used tx.origin instead msg.sender because this function can be call by deploy function
    function totalDeployed() public view returns(uint) {
        uint balance;
        for(uint i=0; i<usersCostCenters[tx.origin].length; ++i) {
            balance += usersStorageArea[tx.origin][usersCostCenters[tx.origin][i]];
        }
        return balance;
    }

}