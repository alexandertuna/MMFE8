library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use IEEE.STD_LOGIC_UNSIGNED.all;
library UNISIM;
use UNISIM.VCOMPONENTS.ALL;

package vmm_pkg is

    type array_8x32bit  is array ( 0 to 7)  of std_logic_vector( 31 downto 0);
    type array_Int_8  is array ( 0 to 7)  of integer;
    type array_8x38bit  is array ( 0 to 7)  of std_logic_vector( 37 downto 0);
	type array_64x32bit  is array ( 0 to 63)  of std_logic_vector( 31 downto 0);
	type array_8x11bit  is array ( 0 to 7)  of std_logic_vector( 10 downto 0);
	type array_8x10bit  is array ( 0 to 7)  of std_logic_vector( 9 downto 0);
	type array_80x32bit  is array ( 0 to 79)  of std_logic_vector( 31 downto 0);
	type array_8x4bit  is array ( 0 to 7)  of std_logic_vector( 3 downto 0);

end vmm_pkg;
