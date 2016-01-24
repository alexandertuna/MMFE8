--
--        acquisition reset
--  ENA -------------------- (0) 
--             -----
--  WEN -------     --------
--

-- IEEE VHDL standard library:
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use IEEE.std_logic_arith.all;
use IEEE.numeric_bit.all;
use IEEE.std_logic_unsigned.all;

library UNISIM;
use UNISIM.vcomponents.all;

entity vmm_acq_reset is
	port(  clk                 : in std_logic;   -- 100MHz
	       rst                 : in std_logic;   -- reset
	       acq_rst             : in std_logic ;  -- from control register. a pulse
		   vmm_wen             : out std_logic;  -- these will be anded with same from other while running sm
		   vmm_ena             : out std_logic;  -- these will be anded with same from other while running sm
		   vmm_acq_rst_running : out std_logic   -- these will be anded with same from other while running sm
		);
end vmm_acq_reset ;

architecture beh of vmm_acq_reset is

	signal acq_reset_counter_max : std_logic_vector(31 downto 0) := x"00000004"; --fast
	signal acq_reset_counter : std_logic_vector(31 downto 0) := x"00000000";


	signal state_nxt : std_logic_vector(2 downto 0);


	signal vmm_wen_int : std_logic;
	signal vmm_ena_int : std_logic;
	signal acq_rst_int : std_logic; 
	signal acq_rst_d   : std_logic;
	signal vmm_acq_rst_running_int : std_logic;
	
begin

--	process( clk, rst, acq_rst, acq_rst_int)
--	begin
--	    if ( rising_edge( clk) ) then
--		   if (rst = '1') then
--	            acq_rst_int <= '0' ;
--		   else 
--		       if (acq_rst = '1') then
--					acq_rst_int <= '1';
--			   else
--			        acq_rst_int <= '0';
--			   end if ;
--		   end if ;
--		end if;
--	end process ;

     process (clk, acq_rst)
     --  this process is an edge detect for acq_rst
         begin
         if rising_edge ( clk) then
             acq_rst_d <= acq_rst;
         end if;
         acq_rst_int <= ((not acq_rst_d) and acq_rst);
     end process; 
     
	process( clk, state_nxt, rst, acq_rst_int, vmm_ena_int, vmm_wen_int)
	begin
		if ( rising_edge( clk)) then       --100MHz
			if (rst = '1') then
				state_nxt <= (others=>'0') ;
				vmm_wen_int <= '0' ;
				vmm_ena_int <= '0' ;
                vmm_acq_rst_running_int <= '0' ;
				acq_reset_counter  <= (others=>'0') ;
			else
					case state_nxt is 
						when "000" => 
                                    vmm_wen_int <= '0' ;
                                    vmm_ena_int <= '0' ;
                                    vmm_acq_rst_running_int <= '0' ;
                                    
                                    if (acq_rst_int = '1') then
                                        state_nxt <= "001" ;                                    
                                        acq_reset_counter  <= (others=>'0') ;
                                    else    
                                        state_nxt <= "000" ;
                                    end if ;
                                    
						when "001" => 
                                    vmm_wen_int <= '0' ;
                                    vmm_ena_int <= '0' ;
                                    vmm_acq_rst_running_int <= '1' ;
                                                    
									if( acq_reset_counter = acq_reset_counter_max) then
                                        state_nxt <= "010" ;                                    
                                        acq_reset_counter  <= (others => '0') ;
                                    else    
                                        state_nxt <= "001" ;
                                        acq_reset_counter <= acq_reset_counter + '1';
                                    end if ;

						when "010" => 
									    vmm_wen_int <= '1' ;
								        vmm_ena_int <= '0' ;
						                vmm_acq_rst_running_int <= '1' ;

										if( acq_reset_counter = acq_reset_counter_max) then
                                            state_nxt <= "011" ;                                    
                                            acq_reset_counter  <= (others => '0') ;
                                        else    
                                            state_nxt <= "010" ;
                                            acq_reset_counter <= acq_reset_counter + '1';
                                        end if ;


--										if( acq_reset_counter = acq_reset_counter_max) then
--										    if( acq_rst = '0') then 
--                                                state_nxt <= "011" ;                                    
--                                                acq_reset_counter  <= (others => '0') ;
--                                            else
--                                                state_nxt <= "010" ;
--                                            end if;
--                                        else    
--                                            state_nxt <= "010" ;
--                                            acq_reset_counter <= acq_reset_counter + '1';
--                                        end if ;
                                           
						when "011" => 
										  vmm_wen_int <= '0';
						                  vmm_ena_int <= '0';
						                  vmm_acq_rst_running_int <= '1';
						                  
										if( acq_reset_counter = acq_reset_counter_max) then
                                              state_nxt <= "000" ;                                    
                                              acq_reset_counter  <= (others => '0') ;
                                          else    
                                              state_nxt <= "011" ;
                                              acq_reset_counter <= acq_reset_counter + '1';
                                          end if ;

						when others =>
						              	  vmm_wen_int <= '0';
						                  vmm_ena_int <= '0';
						                  vmm_acq_rst_running_int <= '0';
										  state_nxt <= (others=>'0');
										  acq_reset_counter <= (others => '0');
					end case ;
			end if ;
	   end if;
	end process ;
	
	vmm_wen <= vmm_wen_int ;
	vmm_ena <= vmm_ena_int ;
	vmm_acq_rst_running <= vmm_acq_rst_running_int;

end beh ;
