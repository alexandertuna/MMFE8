----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 07/06/2015 05:57:35 PM
-- Design Name: 
-- Module Name: leaky_readout - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
use IEEE.NUMERIC_STD.ALL;

use IEEE.std_logic_unsigned.all;    --kg added to make rd_delay_cntr

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

-- read the data fifo from one vmm when there is an external trigger
-- convert the vmm bcid data from gray code to binary
-- only keep data within a certain bcid and turn range
-- write the same data out to the pending fifo
-- the pending fifo data will be readout via axi

entity leaky_readout is
    Port ( 
       clk_200                  : in STD_LOGIC;
       axi_clk                  : in STD_LOGIC;
       reset                    : in STD_LOGIC;
--     signals from external_trigger    
       ext_trigger_pulse        : in STD_LOGIC;
       busy_from_ext_trigger    : in STD_LOGIC;
       bcid_corrected           : in STD_LOGIC_VECTOR (11 downto 0);
       bcid_corrected_m1        : in STD_LOGIC_VECTOR (11 downto 0);
       bcid_corrected_m2        : in STD_LOGIC_VECTOR (11 downto 0);
       bcid_corrected_m3        : in STD_LOGIC_VECTOR (11 downto 0);
       bcid_corrected_m4        : in STD_LOGIC_VECTOR (11 downto 0);
       bcid_corrected_m5        : in STD_LOGIC_VECTOR (11 downto 0);
       bcid_corrected_p1        : in STD_LOGIC_VECTOR (11 downto 0);
       bcid_corrected_p2        : in STD_LOGIC_VECTOR (11 downto 0);
       bcid_corrected_p3        : in STD_LOGIC_VECTOR (11 downto 0);
       bcid_corrected_p4        : in STD_LOGIC_VECTOR (11 downto 0);
       bcid_corrected_p5        : in STD_LOGIC_VECTOR (11 downto 0);                      
       turn_counter_ext_trigger  : in STD_LOGIC_VECTOR (15 downto 0);
-- signals from the data fifo
       data_fifo_rd_en               : buffer STD_LOGIC;
       data_fifo_dout                : in STD_LOGIC_VECTOR(31 DOWNTO 0); --reading from
       data_fifo_empty               : in STD_LOGIC;
       --data_fifo_rd_count            : buffer STD_LOGIC_VECTOR(10 DOWNTO 0); --Currently not connect to anything
       --data_fifo_wr_count            : buffer STD_LOGIC_VECTOR(10 DOWNTO 0); --Currently not connect to anything      
-- axi      
       axi_pop_vmm1                  : in std_logic;                              
       axi_rdata_ls_vmm1             : out std_logic_vector(31 downto 0);
       axi_rdata_rcnt_vmm1           : out std_logic_vector(31 downto 0)             
   );
end leaky_readout;

architecture Behavioral of leaky_readout is

-- components are here

--COMPONENT ila_leaky
--    PORT(
--        clk     : in std_logic;
--        probe0  : in std_logic_vector( 3 downto 0);
--        probe1  : in std_logic_vector( 11 downto 0);    
--        probe2  : in std_logic_vector( 11 downto 0);
--        probe3  : in std_logic_vector( 11 downto 0);
--        probe4  : in std_logic_vector( 15 downto 0);
--        probe5  : in std_logic_vector( 31 downto 0);
--        probe6  : in std_logic_vector( 11 downto 0);
--        probe7  : in std_logic_vector( 7 downto 0);
--        probe8  : in std_logic_vector( 11 downto 0);
--        probe9  : in std_logic_vector( 15 downto 0);
--        probe10 : in std_logic_vector( 31 downto 0);
--        probe11 : in std_logic_vector( 31 downto 0)
--    );
--END COMPONENT;
    
COMPONENT fifo_leaky
    PORT (
        rst : IN STD_LOGIC;
        wr_clk : IN STD_LOGIC;
        rd_clk : IN STD_LOGIC;
        din : IN STD_LOGIC_VECTOR( 31 DOWNTO 0);
        wr_en : IN STD_LOGIC;
        rd_en : IN STD_LOGIC;
        dout : OUT STD_LOGIC_VECTOR( 31 DOWNTO 0);
        full : OUT STD_LOGIC;
        almost_full : OUT STD_LOGIC;
        empty : OUT STD_LOGIC;
        almost_empty : OUT STD_LOGIC;
--        rd_data_count : OUT STD_LOGIC_VECTOR( 10 DOWNTO 0);
--        wr_data_count : OUT STD_LOGIC_VECTOR( 10 DOWNTO 0)
        rd_data_count : OUT STD_LOGIC_VECTOR( 9 DOWNTO 0);
        wr_data_count : OUT STD_LOGIC_VECTOR( 9 DOWNTO 0)
    );
END COMPONENT;

-- signals are here
	signal data_fifo_words_to_read        : STD_LOGIC_VECTOR(10 DOWNTO 0);
	signal data_fifo_word_1               : STD_LOGIC_VECTOR(31 DOWNTO 0);
	signal data_fifo_word_2               : STD_LOGIC_VECTOR(31 DOWNTO 0);
	signal turn_counter_in_data           : STD_LOGIC_VECTOR (15 DOWNTO 0);
	signal bcid_in_data_binary            : STD_LOGIC_VECTOR (11 DOWNTO 0);
	signal bcid_in_data_gray              : STD_LOGIC_VECTOR (11 DOWNTO 0);
    signal leaky_state                    : STD_LOGIC_VECTOR(7 DOWNTO 0);
    signal readout_fifo_wr_count          : STD_LOGIC_VECTOR(10 DOWNTO 0);
    signal readout_fifo_din               : STD_LOGIC_VECTOR(31 DOWNTO 0);
    signal readout_fifo_wr_en             : STD_LOGIC;
    
    --kg read delay counter
    signal rd_delay_cntr	   : std_logic_vector(31 downto 0);
    
     -- std_logic_vector signals for ILA
    signal ext_trigger_pulse_i        : std_logic;
    signal bcid_corrected_i           : std_logic_vector(11 downto 0);
    signal bcid_corrected_m1_i        : std_logic_vector(11 downto 0);
    signal bcid_corrected_p1_i        : std_logic_vector(11 downto 0);
    signal turn_counter_ext_trigger_i : std_logic_vector(15 downto 0);
    signal data_fifo_rd_en_i          : std_logic;
    signal data_fifo_dout_i           : std_logic_vector(31 downto 0);
    signal axi_pop_vmm1_i             : std_logic;                               
    
    signal bcid_in_data_binary_i      : std_logic_vector(11 DOWNTO 0);  --unsigned above
    signal leaky_state_i              : std_logic_vector(7 DOWNTO 0);
    signal readout_fifo_wr_en_i       : std_logic;
    signal bcid_in_data_gray_i        : std_logic_vector(11 DOWNTO 0);  --unsigned above
    signal turn_counter_in_data_i     : std_logic_vector(15 DOWNTO 0);  --unsigned above
	signal data_fifo_word_1_i         : STD_LOGIC_VECTOR(31 DOWNTO 0);
    signal data_fifo_word_2_i         : STD_LOGIC_VECTOR(31 DOWNTO 0);   

    -- signals for ILA probes  
    signal probe0_i  : std_logic_vector( 3 downto 0);
    signal probe1_i  : std_logic_vector( 11 downto 0);    
    signal probe2_i  : std_logic_vector( 11 downto 0);
    signal probe3_i  : std_logic_vector( 11 downto 0);
    signal probe4_i  : std_logic_vector( 15 downto 0);
    signal probe5_i  : std_logic_vector( 31 downto 0);
    signal probe6_i  : std_logic_vector( 11 downto 0);
    signal probe7_i  : std_logic_vector( 7 downto 0);
    signal probe8_i : std_logic_vector( 11 downto 0);
    signal probe9_i : std_logic_vector( 15 downto 0);
    signal probe10_i : STD_LOGIC_VECTOR( 31 DOWNTO 0);
    signal probe11_i : STD_LOGIC_VECTOR( 31 DOWNTO 0);

    -- Attributes 
    attribute keep : string;
    attribute mark_debug : string;
    attribute keep of ext_trigger_pulse_i        : signal is "true";
    attribute keep of bcid_corrected_i           : signal is "true";
    attribute keep of bcid_corrected_m1_i        : signal is "true";
    attribute keep of bcid_corrected_p1_i        : signal is "true";    
    attribute keep of turn_counter_ext_trigger_i : signal is "true";
    attribute keep of data_fifo_rd_en_i          : signal is "true";
    attribute keep of data_fifo_dout_i           : signal is "true";
    attribute keep of axi_pop_vmm1_i             : signal is "true";    
    attribute keep of bcid_in_data_binary_i      : signal is "true";
    attribute keep of leaky_state_i              : signal is "true";
    attribute keep of readout_fifo_wr_en_i       : signal is "true";
    attribute keep of bcid_in_data_gray_i        : signal is "true";
    attribute keep of turn_counter_in_data_i     : signal is "true";
    attribute keep of data_fifo_word_1_i         : signal is "true";
    attribute keep of data_fifo_word_2_i         : signal is "true";    
    attribute mark_debug of ext_trigger_pulse_i        : signal is "true";
    attribute mark_debug of bcid_corrected_i           : signal is "true";
    attribute mark_debug of bcid_corrected_m1_i        : signal is "true";
    attribute mark_debug of bcid_corrected_p1_i        : signal is "true";    
    attribute mark_debug of turn_counter_ext_trigger_i : signal is "true";
    attribute mark_debug of data_fifo_rd_en_i          : signal is "true";
    attribute mark_debug of data_fifo_dout_i           : signal is "true";
    attribute mark_debug of axi_pop_vmm1_i             : signal is "true";
    attribute mark_debug of bcid_in_data_binary_i      : signal is "true";
    attribute mark_debug of leaky_state_i              : signal is "true";
    attribute mark_debug of readout_fifo_wr_en_i       : signal is "true";
    attribute mark_debug of bcid_in_data_gray_i        : signal is "true";
    attribute mark_debug of turn_counter_in_data_i     : signal is "true";
    attribute mark_debug of data_fifo_word_1_i         : signal is "true";
    attribute mark_debug of data_fifo_word_2_i         : signal is "true";

    
-- main code is here

begin

-- this is a clocked process
process( clk_200, reset)

	begin

		if rising_edge( clk_200) then
			if( reset = '1') then                     -- initialize here
			    rd_delay_cntr <= (others =>'0');      --kg cntr set to zero
			else
			    case leaky_state is
		   	        when x"00" =>                     -- wait for the external trigger and see if there is data to readout
                      if (ext_trigger_pulse = '1') then
                          rd_delay_cntr <= (others =>'0');      --jh cntr set to zero
                          leaky_state <= x"01";
                      else                  
                          leaky_state <= x"00";
                      end if;
                                                                    --kg
                    when x"01" =>                                   --wait until data is written before continuing
                        if (rd_delay_cntr = x"00000400") then       --if delayed for long enough
                            leaky_state <= x"02";                   --move to next state
                        else
                            rd_delay_cntr <= rd_delay_cntr + '1';   --else increase counter by 1
                        end if;
                      
		   	        when x"02" =>
		   	          if (data_fifo_empty = '0') then                 -- make sure the fifo is not empty
					       data_fifo_rd_en <= '1';                    -- read word 1 from the fifo
						   data_fifo_word_1 <= data_fifo_dout;             -- this is word 1 from the fifo
                           leaky_state <= x"03";
                      else
                            -- go back to the beginning if the fifo is empty
                            leaky_state <= x"00";
                      end if;                  
                    when x"03" =>                                   
					     data_fifo_rd_en <= '0';                      -- disable the read
						 leaky_state <= x"04";						 
                    when x"04" =>                                    
				         data_fifo_rd_en <= '1';                      -- read word 2 from the fifo
						 data_fifo_word_2 <= data_fifo_dout;               -- this is word 2 from the fifo
						 leaky_state <= x"05";
                    when x"05" =>                                                      
                         data_fifo_rd_en <= '0';                      -- disable the read
                         leaky_state <= x"06";						                
                    when x"06" =>                                     -- kill some time to make sure gray code conversion is done
                         data_fifo_rd_en <= '0';                               
                         leaky_state <= x"07";
                    when x"07" =>                                     -- kill some time to make sure gray code conversion is done
                         data_fifo_rd_en <= '0';                               
                         leaky_state <= x"08";  
                    when x"08" =>                                      --  here we check if the bcid and turn number in the data
                                                                       --  are in the range of bcid and turn number of the external
                                                                       --  trigger 
                        if ( 
                             ( (bcid_in_data_binary = bcid_corrected) or
                               (bcid_in_data_binary = bcid_corrected_m1) or
                               (bcid_in_data_binary = bcid_corrected_m2) or
                               (bcid_in_data_binary = bcid_corrected_m3) or
                               (bcid_in_data_binary = bcid_corrected_m4) or
                               (bcid_in_data_binary = bcid_corrected_p1) or
                               (bcid_in_data_binary = bcid_corrected_p2) or
                               (bcid_in_data_binary = bcid_corrected_p3) or
                               (bcid_in_data_binary = bcid_corrected_p4) ) 
                               and 
                               (turn_counter_in_data = turn_counter_ext_trigger) 
                               ) then                              
						 leaky_state <= x"09";                         -- keep this data
						else
                          leaky_state <= x"02";                        -- do not keep this data
                        end if;
                   when x"09" =>                         
                         readout_fifo_din <= data_fifo_word_1;
                         readout_fifo_wr_en <= '1';                   -- write word 1 to the readout (pending) fifo 
                         leaky_state <= x"0A";             
                   when x"0A" =>                                      
                        readout_fifo_wr_en <= '0';                    -- stop write
                        leaky_state <= x"0B";               
                   when x"0B" =>
				        readout_fifo_din <= data_fifo_word_2;
                        readout_fifo_wr_en <= '1';                    -- write word 2 to the readout (pending) fifo
                        leaky_state <= x"0C"; 
                   when x"0C" =>
                        readout_fifo_wr_en <= '0';                    -- stop write
                        leaky_state <= x"02";                         -- return to state 2                   
		   	       when others => 				                      -- return to the initial state and start over
                        leaky_state <= x"00";
--  other things here                        
                end case;
            end if;
        end if;
	end process ;

--  this is a combinatorial process
    process (bcid_in_data_gray, bcid_in_data_binary)
        begin
--  this is one method    
      bcid_in_data_binary(11) <= bcid_in_data_gray(11);                                                        
      bcid_in_data_binary(10) <= bcid_in_data_binary(11) xor bcid_in_data_gray(10);
      bcid_in_data_binary(9)  <= bcid_in_data_binary(10) xor bcid_in_data_gray(9);                         
      bcid_in_data_binary(8)  <= bcid_in_data_binary(9) xor bcid_in_data_gray(8); 
      bcid_in_data_binary(7)  <= bcid_in_data_binary(8) xor bcid_in_data_gray(7); 
      bcid_in_data_binary(6)  <= bcid_in_data_binary(7) xor bcid_in_data_gray(6); 
      bcid_in_data_binary(5)  <= bcid_in_data_binary(6) xor bcid_in_data_gray(5);
      bcid_in_data_binary(4)  <= bcid_in_data_binary(5) xor bcid_in_data_gray(4); 
      bcid_in_data_binary(3)  <= bcid_in_data_binary(4) xor bcid_in_data_gray(3); 
      bcid_in_data_binary(2)  <= bcid_in_data_binary(3) xor bcid_in_data_gray(2); 
      bcid_in_data_binary(1)  <= bcid_in_data_binary(2) xor bcid_in_data_gray(1); 
      bcid_in_data_binary(0)  <= bcid_in_data_binary(1) xor bcid_in_data_gray(0);
      
--  here is an alternative method
--  variables are defined inside a process
--      variable bv : std_logic_vector(11 downto 0);
--      bv(11) <= bcid_in_data_gray(11); 
--      for i in 10 downto 0 loop
--         bv(i) :=  bv(i+1) xor bcid_in_data_gray(i)
--      end loop; 
--      bcid_in_data_binary <= bv;

        end process ;

--  these are assignments that don't have to be in the clocked process
--  we need to check how these are stored in the data
    bcid_in_data_gray <= STD_LOGIC_VECTOR(data_fifo_word_2(11 downto 0)); 
    turn_counter_in_data <= STD_LOGIC_VECTOR(data_fifo_word_2(27 downto 12));
            
--  vmm data get written to the data fifo in vmm_cfg
--  this is the read fifo, that we sometimes call the pending read fifo

fifo_leaky_inst : fifo_leaky
    PORT MAP (
        rst             => reset,
        wr_clk          => clk_200,
        rd_clk          => axi_clk,
        din             => readout_fifo_din,
        wr_en           => readout_fifo_wr_en,
        rd_en           => axi_pop_vmm1,
        dout            => axi_rdata_ls_vmm1,
        full            => open,
        almost_full     => open,
        empty           => open,
        almost_empty    => open,
--        rd_data_count   => axi_rdata_rcnt_vmm1( 10 downto 0),
--        wr_data_count   => readout_fifo_wr_count( 10 downto 0)
        rd_data_count   => axi_rdata_rcnt_vmm1( 9 downto 0),
        wr_data_count   => readout_fifo_wr_count( 9 downto 0)
    );
  
axi_rdata_rcnt_vmm1(31 downto 11) <= (others => '0');  -- Optimizer will take care of this. 

    -- Variables for ILA
    ext_trigger_pulse_i        <= ext_trigger_pulse;
    bcid_corrected_i           <= std_logic_vector(bcid_corrected);
    bcid_corrected_m1_i        <= std_logic_vector(bcid_corrected_m1);
    bcid_corrected_p1_i        <= std_logic_vector(bcid_corrected_p1);
    turn_counter_ext_trigger_i <= std_logic_vector(turn_counter_ext_trigger);
    data_fifo_rd_en_i          <= data_fifo_rd_en;
    data_fifo_dout_i           <= std_logic_vector(data_fifo_dout);
    axi_pop_vmm1_i             <= axi_pop_vmm1;                                
    bcid_in_data_binary_i      <= std_logic_vector(bcid_in_data_binary);
    leaky_state_i              <= std_logic_vector(leaky_state);
    readout_fifo_wr_en_i       <= readout_fifo_wr_en;
    bcid_in_data_gray_i        <= std_logic_vector(bcid_in_data_gray);      --kg maybe use std_logic_vector(unsigned(bcid_in_data_gray)+1)?;
    turn_counter_in_data_i     <= std_logic_vector(turn_counter_in_data);
    data_fifo_word_1_i         <= std_logic_vector(data_fifo_word_1);
    data_fifo_word_2_i         <= std_logic_vector(data_fifo_word_2);

--    -- Assign ILA probes
--    probe0_i    <= ext_trigger_pulse_i & data_fifo_rd_en_i & axi_pop_vmm1_i & readout_fifo_wr_en_i;
--    probe1_i    <= bcid_corrected_i;
--    probe2_i    <= bcid_corrected_m1_i;
--    probe3_i    <= bcid_corrected_p1_i;
--    probe4_i    <= turn_counter_ext_trigger_i;
--    probe5_i    <= data_fifo_dout_i;
--    probe6_i    <= bcid_in_data_binary_i;
--    probe7_i    <= leaky_state_i;
--    probe8_i    <= bcid_in_data_gray_i;
--    probe9_i    <= turn_counter_in_data_i;
--    probe10_i   <= data_fifo_word_1_i;
--    probe11_i   <= data_fifo_word_2_i;

    
--ila_leaky_inst : ila_leaky
--PORT MAP(
--    clk     => clk_200,
--    probe0  => probe0_i,
--    probe1  => probe1_i, 
--    probe2  => probe2_i,
--    probe3  => probe3_i,
--    probe4  => probe4_i,
--    probe5  => probe5_i,    
--    probe6  => probe6_i,
--    probe7  => probe7_i,
--    probe8  => probe8_i,
--    probe9  => probe9_i,
--    probe10 => probe10_i,
--    probe11 => probe11_i
--);


end Behavioral;
