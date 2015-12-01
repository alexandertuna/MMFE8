----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 06/28/2015 09:00:17 AM
-- Design Name: 
-- Module Name: external_trigger - Behavioral
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

use IEEE.std_logic_unsigned.all;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
library UNISIM;
use UNISIM.VComponents.all;

entity external_trigger is
    Port ( clk_40                   : in STD_LOGIC;
           reset_bcid_counter       : in STD_LOGIC;
           ext_trigger_in           : in STD_LOGIC;
           ext_trigger_pulse_o        : out STD_LOGIC;
           busy_from_ext_trigger_o    : out STD_LOGIC;
           bcid_counter_o             : out STD_LOGIC_VECTOR (11 downto 0);
           bcid_captured_o            : out STD_LOGIC_VECTOR (11 downto 0);
           bcid_corrected_o           : out STD_LOGIC_VECTOR (11 downto 0);
           bcid_corrected_m1        : out STD_LOGIC_VECTOR (11 downto 0);
           bcid_corrected_m2        : out STD_LOGIC_VECTOR (11 downto 0);
           bcid_corrected_m3        : out STD_LOGIC_VECTOR (11 downto 0);
           bcid_corrected_m4        : out STD_LOGIC_VECTOR (11 downto 0);
           bcid_corrected_m5        : out STD_LOGIC_VECTOR (11 downto 0);
           bcid_corrected_p1        : out STD_LOGIC_VECTOR (11 downto 0);
           bcid_corrected_p2        : out STD_LOGIC_VECTOR (11 downto 0);
           bcid_corrected_p3        : out STD_LOGIC_VECTOR (11 downto 0);
           bcid_corrected_p4        : out STD_LOGIC_VECTOR (11 downto 0);
           bcid_corrected_p5        : out STD_LOGIC_VECTOR (11 downto 0);                                            
           turn_counter_o             : out STD_LOGIC_VECTOR (15 downto 0);
           turn_counter_captured_o    : out STD_LOGIC_VECTOR (15 downto 0)
       );

end external_trigger;

architecture Behavioral of external_trigger is

-- components are here

--COMPONENT ila_ext_trig

--PORT (
--	clk : IN STD_LOGIC;

--	probe0 : IN STD_LOGIC_VECTOR( 3 DOWNTO 0); 
--	probe1 : IN STD_LOGIC_VECTOR( 11 DOWNTO 0); 
--	probe2 : IN STD_LOGIC_VECTOR( 11 DOWNTO 0); 
--	probe3 : IN STD_LOGIC_VECTOR( 11 DOWNTO 0); 
--	probe4 : IN STD_LOGIC_VECTOR( 15 DOWNTO 0);
--	probe5 : IN STD_LOGIC_VECTOR( 15 DOWNTO 0)
--);
--END COMPONENT  ;

-- signals are here

	constant bcid_offset           : STD_LOGIC_VECTOR (11 downto 0)   := x"716"; --x"005";
	--jh added first '0' to x"0FA0"; decleration because of synth error...
	constant busy_width            : STD_LOGIC_VECTOR (15 downto 0)	:= x"0FA0";   -- time busy is set (1 ms) busy_width = f_clk / (1/t_desired) --kg changed to 1/10 what it was
	constant trigger_pulse_width   : STD_LOGIC_VECTOR (3 downto 0) := x"A"; --trigger pulse width of 250ns. trigger_pulse_width = t_desired / t_clk
	signal trigger                 : std_logic;
	signal trigger_pulse           : std_logic;
	signal busy                    : std_logic;
	signal busy_count              : STD_LOGIC_VECTOR (15 downto 0);
	signal trigger_pulse_count     : STD_LOGIC_VECTOR(3 downto 0);
	signal trigger_was_low         : std_logic; --flag to check that ext_trigger has been low after busy is done. This eliminates problem of trigger
										-- pulse firing again once busy goes low if ext_trigger never goes low.
	
    signal reset_bcid_counter_i    : STD_LOGIC;
    signal ext_trigger_in_i        : STD_LOGIC;
    signal ext_trigger_pulse       : STD_LOGIC;
    signal ext_trigger_pulse_i     : STD_LOGIC;
    signal busy_from_ext_trigger   : STD_LOGIC;
    signal busy_from_ext_trigger_i : STD_LOGIC;
    signal bcid_counter            : STD_LOGIC_VECTOR(11 DOWNTO 0);
    signal bcid_counter_i          : STD_LOGIC_VECTOR(11 DOWNTO 0);
    signal bcid_captured           : STD_LOGIC_VECTOR(11 DOWNTO 0);
    signal bcid_captured_i         : STD_LOGIC_VECTOR(11 DOWNTO 0);
    signal bcid_corrected          : STD_LOGIC_VECTOR(11 DOWNTO 0);
    signal bcid_corrected_i        : STD_LOGIC_VECTOR(11 DOWNTO 0);
    signal turn_counter            : STD_LOGIC_VECTOR(15 DOWNTO 0);
    signal turn_counter_i          : STD_LOGIC_VECTOR(15 DOWNTO 0);
    signal turn_counter_captured   : STD_LOGIC_VECTOR(15 DOWNTO 0);
    signal turn_counter_captured_i : STD_LOGIC_VECTOR(15 DOWNTO 0);
    
    attribute keep : string;
    attribute mark_debug : string;
    attribute keep of reset_bcid_counter_i          : signal is "true";
    attribute keep of ext_trigger_in_i              : signal is "true";
    attribute keep of ext_trigger_pulse_i           : signal is "true";
    attribute keep of busy_from_ext_trigger_i       : signal is "true";    
    attribute keep of bcid_counter_i                : signal is "true";
    attribute keep of bcid_captured_i               : signal is "true";
    attribute keep of bcid_corrected_i              : signal is "true";
    attribute keep of turn_counter_i                : signal is "true";
    attribute keep of turn_counter_captured_i       : signal is "true";
    attribute mark_debug of reset_bcid_counter_i    : signal is "true";
    attribute mark_debug of ext_trigger_in_i        : signal is "true";
    attribute mark_debug of ext_trigger_pulse_i     : signal is "true";
    attribute mark_debug of busy_from_ext_trigger_i : signal is "true";    
    attribute mark_debug of bcid_counter_i          : signal is "true";
    attribute mark_debug of bcid_captured_i         : signal is "true";
    attribute mark_debug of bcid_corrected_i        : signal is "true";
    attribute mark_debug of turn_counter_i          : signal is "true";
    attribute mark_debug of turn_counter_captured_i : signal is "true";
                                                        
	signal probe0_i : STD_LOGIC_VECTOR(3 DOWNTO 0); 
--    signal probe1_i : STD_LOGIC_VECTOR(11 DOWNTO 0); 
--    signal probe2_i : STD_LOGIC_VECTOR(11 DOWNTO 0); 
--    signal probe3_i : STD_LOGIC_VECTOR(11 DOWNTO 0); 
--    signal probe4_i : STD_LOGIC_VECTOR(15 DOWNTO 0);
--    signal probe5_i : STD_LOGIC_VECTOR(15 DOWNTO 0);

begin

	ext_trigger_pulse     <= trigger_pulse;
	busy_from_ext_trigger <= busy;

	process (clk_40, reset_bcid_counter, ext_trigger_in) 
	
	begin
		if (reset_bcid_counter = '1') then
		--  this comes from the state machine that starts the bc clock
			bcid_counter <= x"000";
			turn_counter <= x"0000";
			busy <= '0';
			trigger_pulse <= '0';
			trigger_was_low <= '1';
			
		elsif (rising_edge (clk_40) ) then
						bcid_counter <= bcid_counter + '1';
						if ( bcid_counter = x"fff" ) then
						  turn_counter <= turn_counter + '1';
						end if;
						
			if (busy = '0') then
			--  here comes an external trigger and we were waiting for one
				  if  (ext_trigger_in = '1' and trigger_was_low = '1')then
					-- generate a trigger pulse and busy
					trigger_pulse <= '1';
					busy <= '1';
					trigger_was_low <= '0';
					bcid_captured <= bcid_counter;
					turn_counter_captured <= turn_counter;
					--  here adjust the bcid to reflect the fact that the trigger
					--  may come later than the time of the actual event
                        if (bcid_offset > bcid_counter) then 
                            bcid_corrected <= x"FFF"- bcid_offset + bcid_counter;
                        else 
                            bcid_corrected <= bcid_counter - bcid_offset;
                        end if;
            -- if not busy and no external trigger, continue to wait            
				    elsif (ext_trigger_in = '0') then 
					  trigger_was_low <= '1';
				    end if;
			else
			-- here we are in the busy state
			-- keep busy high until the busy width is reached
				if (busy_count >= busy_width - 1) then
					busy <= '0';
				end if;
			
				if (trigger_pulse_count >= trigger_pulse_width - '1') then
					trigger_pulse <= '0';
				end if;
			end if;
		end if;
		
		
	end process;
	
	--time for trigger_pulse
	process (clk_40) 
	begin
	   if clk_40='1' and clk_40'event then
		  if trigger_pulse='0' or reset_bcid_counter = '1' then 
			 trigger_pulse_count <= x"0";
		  elsif trigger_pulse='1' then
			 trigger_pulse_count <= trigger_pulse_count + '1';
		  end if;
	   end if;
	end process; 
	
	--time for busy
	process (clk_40) 
	begin
	   if clk_40='1' and clk_40'event then
		  if busy ='0' or reset_bcid_counter = '1' then 
			 busy_count <= x"0000";
		  elsif busy='1' then
			 busy_count <= busy_count + '1';
		  end if;
	   end if;
	end process; 

--  need to account for bc counter boundaries
    bcid_corrected_m1 <= bcid_corrected - b"000000000001";
    bcid_corrected_m2 <= bcid_corrected - b"000000000010";    
    bcid_corrected_m3 <= bcid_corrected - b"000000000011";
    bcid_corrected_m4 <= bcid_corrected - b"000000000100";
    bcid_corrected_m5 <= bcid_corrected - b"000000000101";
    bcid_corrected_p1 <= bcid_corrected + b"000000000001";
    bcid_corrected_p2 <= bcid_corrected + b"000000000010";    
    bcid_corrected_p3 <= bcid_corrected + b"000000000011";
    bcid_corrected_p4 <= bcid_corrected + b"000000000100";
    bcid_corrected_p5 <= bcid_corrected + b"000000000101";    

    reset_bcid_counter_i    <= reset_bcid_counter;
    ext_trigger_in_i        <= ext_trigger_in;
    ext_trigger_pulse_i     <= ext_trigger_pulse;
    ext_trigger_pulse_o     <= ext_trigger_pulse;
    busy_from_ext_trigger_i <= busy_from_ext_trigger;
    busy_from_ext_trigger_o <= busy_from_ext_trigger;
    bcid_counter_i          <= bcid_counter;
    bcid_counter_o          <= bcid_counter;
    bcid_captured_i         <= bcid_captured;
    bcid_captured_o         <= bcid_captured;
    bcid_corrected_i        <= bcid_corrected;
    bcid_corrected_o        <= bcid_corrected;
    turn_counter_i          <= turn_counter;
    turn_counter_o          <= turn_counter;
    turn_counter_captured_i <= turn_counter_captured;
    turn_counter_captured_o <= turn_counter_captured;
    
-- assign probes
--        probe0_i <= reset_bcid_counter_i & ext_trigger_in_i & ext_trigger_pulse_i & busy_from_ext_trigger_i ;

--ila_ext_trig_inst : ila_ext_trig
--    PORT MAP (
--        clk => clk_40,
        
--        probe0 => probe0_i,
--        probe1 => bcid_counter_i,
--        probe2 => bcid_captured_i,
--        probe3 => bcid_corrected_i,
--        probe4 => turn_counter_i,
--        probe5 => turn_counter_captured_i
--    );            
end Behavioral;
