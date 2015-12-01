--
-- VMM registers and configuration
-- this block handles the 1616 bit serial configuration
-- streams
--

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;
-- use IEEE.std_logic_arith.all;
-- use IEEE.numeric_bit.all;
use IEEE.std_logic_unsigned.all;
use IEEE.std_logic_unsigned.all;
--use IEEE.std_logic_signed.all;

Library UNISIM;
use UNISIM.vcomponents.all;

entity vmm_daq is

port
(
    vmm_clk_200             : in 	STD_LOGIC; 
	reset					: in 	STD_LOGIC;
	vmmNumber					: in 	STD_LOGIC_VECTOR( 2 downto 0);

    vmm_data0                 : in     STD_LOGIC;
    vmm_data1                 : in    std_logic;
    vmm_art                   : in    std_logic;
    turn_counter              : in    std_logic_vector(15 downto 0); 

    vmm_cktk_daq_en  	      : out   std_logic ;
    vmm_ckdt_en  	          : out   std_logic ;

    vmm_ckdt                  : in    std_logic ;
    vmm_ckart                 : in    std_logic ;

    din                         : buffer   std_logic_vector( 31 downto 0);
    dt_cntr_intg0               : buffer   integer;
    dt_cntr_intg1               : buffer   integer;
    vmm_data_buf                : buffer   std_logic_vector( 37 downto 0);
    
  
    rd_clk  	              : in   std_logic ;
    empty  	                  : out   std_logic ;
--    rd_data_count   	      : out   std_logic_vector( 10 downto 0);
--    wr_data_count             : out   std_logic_vector( 10 downto 0);
    rd_data_count   	      : out   std_logic_vector( 9 downto 0);
    wr_data_count             : out   std_logic_vector( 9 downto 0);
    rd_en                     : in   std_logic;
    dout                      : out   std_logic_vector( 31 DOWNTO 0)
);
	
end vmm_daq;

architecture rtl of vmm_daq is


COMPONENT fifo_daq
    PORT (
          clk : IN STD_LOGIC;
          rst : IN STD_LOGIC;
          din : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
          wr_en : IN STD_LOGIC;
          rd_en : IN STD_LOGIC;
          dout : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
          full : OUT STD_LOGIC;
          empty : OUT STD_LOGIC
    );
END COMPONENT; 

--     SIGNAL vmm_data0_Q         :   STD_LOGIC := '0';
--     SIGNAL vmm_data0_CLR       :   STD_LOGIC := '0';

    signal dt_state             : std_logic_vector( 3 downto 0) := (others => '0');
    signal dt_reset             : std_logic := '0';
    signal art_reset            : std_logic := '0';
    signal wr_en                : std_logic := '0';
    signal dt_done              : std_logic := '0';

    signal art_state             : std_logic_vector( 3 downto 0) := (others => '0');
    signal art_data             : std_logic_vector( 7 downto 0) := (others => '0');
    signal art_done              : std_logic := '0';
  
    SIGNAL vmm_data_buf_i         :  STD_LOGIC_VECTOR( 37 DOWNTO 0) := (OTHERS => '0');
 
    signal dt_cntr_intg          :  integer := 0;


begin
    
    -- acquisition read out to fifo process
	process( vmm_clk_200, reset, vmm_data0, dt_done)

	begin
		if rising_edge( vmm_clk_200) then
			if( reset = '1') then
				dt_state <= (others => '0');        -- init readout seq state
                vmm_cktk_daq_en <= '1';             -- en cktk
                wr_en <= '0';                       -- no fifo writes
                art_reset <= '1';
                dt_reset <= '1';                    -- hold the ro process in reset
                
			else
			    case dt_state is
		   	        when x"0" =>                    -- init the RO sequence
                         vmm_cktk_daq_en <= '1';            -- cktk enabled
                         wr_en <= '0';                      -- no fifo writes
                         dt_reset <= '1';                   -- hold ro process in reset
                         art_reset <= '0';
                         dt_state <= x"1";                 -- go tto wait state
                                         
		   	        when x"1" =>                     --wait for data0
                        if( vmm_data0 = '1') then        -- gotta live one
                            vmm_cktk_daq_en <= '0';         -- turn off the cktk
                            art_reset <= '0';
                            dt_reset <= '0';                -- enable the readout process
                            dt_state <= x"3";              -- start the readout sequence
                        else
                            art_reset <= '0';
                            dt_state <= x"1";              -- else wait
                         end if;                       
                  
-- kjohns removes this state, unclear if it is necessary                  
-- 		   	       when x"2" =>
--                        vmm_cktk_daq_en <= '0';         -- turn off the cktk -- added redundant to make it work -- vivado bug?
--                        dt_state <= x"03";                --start the readout

                   when x"3" =>
                        if( dt_done = '1') then
                            dt_state <= x"4";               
                        else
                            dt_state <= x"3";             -- else we are waiting               
                        end if;

                   when x"4" =>                          -- copy first half of buffer to fifo  
--                        din <= b"000000" & vmm_data_buf( 25 downto 0);  
                        din <= b"000" & vmmNumber & vmm_data_buf( 25 downto 0);  
                        art_reset <= '1';
                        dt_state <= x"5";               

                   when x"5" =>
                        wr_en <= '1';
                        art_reset <= '1';
                        dt_state <= x"6";               

                   when x"6" =>
                        wr_en <= '0';
                        art_reset <= '1';
                        dt_state <= x"7";               

                   when x"7" =>                           -- copy second half of buffer to fifo  
--                        din <= x"beef" & b"0000" & vmm_data_buf( 37 downto 26);
                        din <= b"1011" & turn_counter & vmm_data_buf( 37 downto 26);
                        art_reset <= '1';
                        dt_state <= x"8";               

                   when x"8" =>
                        wr_en <= '1';
                        art_reset <= '0';
                        dt_state <= x"9";               

                   when x"9" =>
                        wr_en <= '0';
                        art_reset <= '0';
                        dt_state <= x"A";               

		   	       when x"A" =>                          -- start the cleanup
                        vmm_cktk_daq_en <= '1';           -- cktk enabled 
        				dt_reset <= '1';                  -- hold ro process in reset
                        art_reset <= '0';
                        dt_state <= x"0";                -- start the readout

                   when others => 
                        vmm_cktk_daq_en <= '1';             -- en cktk
                        wr_en <= '0';                       -- no fifo writes
                        dt_reset <= '1';                    -- hold the ro process in reset
                        art_reset <= '1';
                        dt_state <= (others => '0');        -- init readout seq state
                        
                end case;
            end if;
        end if;
	end process ;

    
     --Clock in data0 and data1 on ckdt
--	process( vmm_ckdt, reset, dt_reset, vmm_data0_C, vmm_data1, dt_cntr_intg0, dt_cntr_intg1)
	process( vmm_ckdt, reset, dt_reset, vmm_data0, vmm_data1, dt_cntr_intg0, dt_cntr_intg1)
     begin
         if rising_edge( vmm_ckdt) then
 
             if( ( reset = '1') or (dt_reset = '1')) then                    -- reset
                   vmm_data_buf <=  (others => '0');
--                   dt_cntr <= (others => '0');
                   dt_cntr_intg0 <= 0;     --use 2 delays at 100MHz, use 200MHz
                   dt_cntr_intg1 <= 1;
                   dt_cntr_intg <= 0;
                   vmm_ckdt_en <= '0';               -- disable ckdt
                   dt_done <= '0';
             
             else
                                
                   case dt_cntr_intg is
                   
                       when 0 =>  -- enable ckdt
                           vmm_ckdt_en <= '1'; 
                           dt_cntr_intg <= dt_cntr_intg + 1;
                       
                       when 1 =>  -- clock 1 sent, no data collected
                                  -- bill says clock will not actually start until next cycle after vmm_ckdt_en
                                  -- that is, it is sent here    
                           dt_cntr_intg <= dt_cntr_intg + 1;  -- but we have to wait for the data to come back from vmm
    
                        when 2 to 18 =>  --  clock 2 - 18 sent, data from clock 1 - 17 collected 
--                           vmm_data_buf( dt_cntr_intg0) <= vmm_data0_C;   
                           vmm_data_buf( dt_cntr_intg0) <= vmm_data0;   
                           vmm_data_buf( dt_cntr_intg1) <= vmm_data1; 
                           vmm_data_buf_i <= vmm_data_buf;                          
                           dt_cntr_intg <= dt_cntr_intg + 1;                                 -- increment the counter
                           dt_cntr_intg0 <= dt_cntr_intg0 + 2;     
                           dt_cntr_intg1 <= dt_cntr_intg1 + 2;                       
                       
                        when 19 => -- clock 19 (last) is sent, data from clock 18 collected
--                           vmm_data_buf( dt_cntr_intg0) <= vmm_data0_C;   
                           vmm_data_buf( dt_cntr_intg0) <= vmm_data0;   
                           vmm_data_buf( dt_cntr_intg1) <= vmm_data1; 
                           vmm_data_buf_i <= vmm_data_buf;                                                      
                           dt_cntr_intg <= dt_cntr_intg + 1;                                 -- increment the counter
                           dt_cntr_intg0 <= dt_cntr_intg0 + 2;     
                           dt_cntr_intg1 <= dt_cntr_intg1 + 2; 
                           vmm_ckdt_en <= '0'; -- disable ckdt, hopefully clock 20 is not sent                     
                           
                        when 20 =>  -- no more clocks are sent, data from clock 19 is collected
--                           vmm_data_buf( dt_cntr_intg0) <= vmm_data0_C;   
                           vmm_data_buf( dt_cntr_intg0) <= vmm_data0;   
                           vmm_data_buf( dt_cntr_intg1) <= vmm_data1;
                           vmm_data_buf_i <= vmm_data_buf;                            
                           dt_cntr_intg <= dt_cntr_intg + 1; 
                           dt_cntr_intg0 <= 0;
                           dt_cntr_intg1 <= 1; 
                           vmm_ckdt_en <= '0'; -- disable ckdt, hopefully clock 20 is not sent
                           
                        when 21 =>
                           dt_done <= '1';  -- end this mess
                           
                        when others =>  
                           vmm_ckdt_en <= '0';   -- continue to disable ckdt
                           dt_cntr_intg <= 22;
    
                   end case;
             end if;
         end if;
     end process ;
        



    --Clock in art_data on ckart
	process( vmm_ckart, reset, art_reset, vmm_art, art_data, art_done)
	begin
        if rising_edge( vmm_ckart) then

            if( ( reset = '1') or (art_reset = '1')) then                    -- reset
                  art_data <=  (others => '0');
                  art_state <= (others => '0');
                  art_done <= '0';

    		else 
                  
		          case art_state is
                
                      when x"0" =>
                          art_done <= '0';
                          if( vmm_art = '1') then    -- check for 1 in art
                              art_state <= x"1";
                              art_data( 0) <= '1';   
                          else
                              art_state <= x"0";
                          end if;                
                        
                      when x"1" =>                    -- store art addX
                          art_done <= '0';
                          art_data( 1) <= vmm_art;
                          art_state <= x"2";
                          
                      when x"2" =>                    -- store art add0
                          art_done <= '0';
                          art_data( 2) <= vmm_art;
                          art_state <= x"3";
                          
                      when x"3" =>                    -- store art add1
                          art_done <= '0';
                          art_data( 3) <= vmm_art;
                          art_state <= x"4";
                          
                      when x"4" =>                    -- store art add2
                          art_done <= '0';
                          art_data( 4) <= vmm_art;
                          art_state <= x"5";
                          
                      when x"5" =>                    -- store art add3
                          art_done <= '0';
                          art_data( 5) <= vmm_art;
                          art_state <= x"6";
                          
                      when x"6" =>                    -- store art add4
                          art_done <= '0';
                          art_data( 6) <= vmm_art;
                          art_state <= x"7";
                              
                      when x"7" =>                    -- store art add5
                          art_done <= '0';
                          art_data( 7) <= vmm_art;
                          art_state <= x"8";
                                  
                      when x"8" =>                    -- finish
                          art_done <= '1';
                          art_state <= x"8";
                                                  
                      when others => 
                          art_done <= '1';
                          art_state <= x"8";
                          
                  end case;
              end if;
          end if;
	end process ;
		


     
--fifo_daq_inst : fifo_daq
--      PORT MAP (
--        rst => reset,
--        wr_clk => vmm_clk_200,
--        rd_clk => vmm_clk_200,
--        din => din,
--        wr_en => wr_en,
--        rd_en => rd_en,
--        dout => dout,
--        full => open,
--        almost_full => open,
--        empty => empty,
--        almost_empty => open,
--        rd_data_count => rd_data_count,
--        wr_data_count => wr_data_count
--      );
      
fifo_daq_inst : fifo_daq
        PORT MAP (
          clk => vmm_clk_200,
          rst => reset,
          din => din,
          wr_en => wr_en,
          rd_en => rd_en,
          dout => dout,
          full => open,
          empty => empty
        );
--        rd_data_count <= b"00000000000";
--        wr_data_count <= b"00000000000";
        rd_data_count <= b"0000000000";
        wr_data_count <= b"0000000000";

end rtl;
  