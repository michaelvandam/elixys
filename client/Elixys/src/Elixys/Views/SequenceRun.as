package Elixys.Views
{
	import Elixys.Assets.Styling;
	import Elixys.JSON.State.State;
	import Elixys.JSON.State.StateSequence;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	import flash.utils.*;
	
	// This sequence run screen is an extension of the base sequence class
	public class SequenceRun extends SequenceBase
	{
		/***
		 * Construction
		 **/
		
		public function SequenceRun(screen:Sprite, pElixys:Elixys, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, pElixys, SEQUENCERUN, attributes, row, inGroup);

			// Set our post string
			m_sPostString = "RUN";
		}

		/***
		 * Loading functions
		 **/
		
		// Loads the next child component and return true or returns false if the load is complete
		public override function LoadNext():Boolean
		{
			// Load the view children first
			if (m_nChildrenLoaded < RUN_LOAD_STEPS)
			{
				// Step 1 is loading the navigation bar
				if (m_nChildrenLoaded == 0)
				{
					LoadNavigationBar("sequencerun_navigationbar_container", NAVIGATION);
				}
				
				// Step 2 is loading the sequencer
				if (m_nChildrenLoaded == 1)
				{
					LoadSequencer("sequencerun_sequencer_container", SEQUENCER);
				}

				// Increment and return
				++m_nChildrenLoaded;
				return true;
			}
			
			// Call the base function to load the base children
			return LoadNextBase(LOAD_STEPS);
		}

		/***
		 * Member functions
		 **/
		
		// Updates the state
		public override function UpdateState(pState:State):void
		{
			// Call the base handler
			super.UpdateState(pState);
		}
		
		/***
		 * Member variables
		 **/

		// Sequence run XML
		protected static const SEQUENCERUN:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND} alignH="fill" alignV="fill">
				<rows gapV="0" border="false" heights="18%,61%,21%" alignH="fill" alignV="fill">
					<frame id="sequencerun_navigationbar_container" alignV="fill" alignH="fill" />
					<rows heights="8%,3%,89%" gapV="0" alignV="fill" alignH="fill">
						<frame id="sequence_title_container" />
						<frame />
						<columns widths="36%,64%" gapH="0" alignV="fill" alignH="fill">
							<rows heights="10%,90%" gapV="0" alignV="fill" alignH="fill">
								<frame background="#00F000" />
								<frame background="#FFFF00" />
							</rows>
							<frame background="#00FF00" />
						</columns>
					</rows>
					<frame id="sequencerun_sequencer_container" alignV="fill" alignH="fill" />
				</rows>
			</frame>;
		
		// Navigation bar XML
		protected static const NAVIGATION:XML =
			<navigationbar alignH="fill" alignV="fill" skin={getQualifiedClassName(blueNavigationBar_mc)} rightpadding="20">
				<navigationbaroption name="SEQUENCER" backgroundskinheightpercent="72" foregroundskinheightpercent="30"
						fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_GRAY1} disabledTextColor={Styling.TEXT_GRAY1}
						backgroundskinup={getQualifiedClassName(mainNav_activeBtnOutline_down)}
						backgroundskindown={getQualifiedClassName(mainNav_activeBtnOutline_down)}
						backgroundskindisabled={getQualifiedClassName(mainNav_activeBtnOutline_down)}
						foregroundskinup={getQualifiedClassName(mainNav_sequencer_active)}
						foregroundskindown={getQualifiedClassName(mainNav_sequencer_down)} 
						foregroundskindisabled={getQualifiedClassName(mainNav_sequencer_disabled)}>
					SEQUENCER
				</navigationbaroption>
				<navigationbaroption name="ABORTRUN" foregroundskinheightpercent="30" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY4}
						foregroundskinup={getQualifiedClassName(seqListNav_editSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_editSequence_down)} 
						foregroundskindisabled={getQualifiedClassName(seqListNav_editSequence_disabled)}>
					ABORT RUN
				</navigationbaroption>
				<navigationbaroption blank="true" />
				<navigationbaroption blank="true" />
				<navigationbaroption blank="true" />
				<navigationbaroption blank="true" />
				<navigationbaroption blank="true" />
			</navigationbar>;
		
		// Sequencer XML
		protected static const SEQUENCER:XML =
			<sequencer mode={StateSequence.RUNTYPE} alignH="fill" alignV="fill"/>;
		
		// Number of steps required to load this object
		public static var RUN_LOAD_STEPS:uint = 2;
		public static var LOAD_STEPS:uint = SequenceBase.BASE_LOAD_STEPS + RUN_LOAD_STEPS;
	}
}
