// SPDX-License-Identifier: MIT

pragma solidity ^0.8;

contract test {
    function b() public view returns (uint256, uint256) {
        return (block.number, block.prevrandao);
    }
}
