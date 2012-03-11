package Elixys.Views
{
	import Elixys.Assets.Styling;
	import Elixys.JSON.State.State;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	import flash.utils.*;
	
	// This sequence edit screen is an extension of the base sequence class
	public class SequenceEdit extends SequenceBase
	{
		/***
		 * Construction
		 **/
		
		public function SequenceEdit(screen:Sprite, pElixys:Elixys, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, pElixys, SEQUENCEEDIT, attributes, row, inGroup);
			
			// Set our post string
			m_sPostString = "EDIT";
		}

		/***
		 * Loading functions
		 **/
		
		// Loads the next child component and return true or returns false if the load is complete
		public override function LoadNext():Boolean
		{
			// Load the edit children first
			if (m_nChildrenLoaded < EDIT_LOAD_STEPS)
			{
				// Step 1 is loading the navigation bar
				if (m_nChildrenLoaded == 0)
				{
					LoadNavigationBar("sequenceedit_navigationbar_container", NAVIGATION);
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

		// Sequence view XML
		protected static const SEQUENCEEDIT:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND} alignH="fill" alignV="fill">
				<rows gapV="0" border="false" heights="18%,82%" alignH="fill" alignV="fill">
					<frame id="sequenceedit_navigationbar_container" alignV="fill" alignH="fill" />
					<frame alignV="fill" alignH="fill" background="#9999FF" />
				</rows>
			</frame>;
		
		// Navigation bar XML
		protected static const NAVIGATION:XML =
			<navigationbar alignH="fill" alignV="fill" skin={getQualifiedClassName(blueNavigationBar_mc)} rightpadding="20">
				<navigationbaroption name="SEQUENCER" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_GRAY3} disabledTextColor={Styling.TEXT_GRAY3}
						foregroundskinup={getQualifiedClassName(mainNav_sequencer_disabled)}
						foregroundskindown={getQualifiedClassName(mainNav_sequencer_down)} 
						foregroundskindisabled={getQualifiedClassName(mainNav_sequencer_disabled)}>
					SEQUENCER
				</navigationbaroption>
				<navigationbaroption name="VIEWSEQUENCE" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY3}
						foregroundskinup={getQualifiedClassName(seqListNav_viewSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_viewSequence_down)} 
						foregroundskindisabled={getQualifiedClassName(seqListNav_viewSequence_disabled)}>
					VIEW SEQUENCE
				</navigationbaroption>
				<navigationbaroption name="RUNSEQUENCE" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY3}
						foregroundskinup={getQualifiedClassName(seqListNav_runSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_runSequence_down)}
						foregroundskindisabled={getQualifiedClassName(seqListNav_runSequence_disabled)}>
					RUN SEQUENCE
				</navigationbaroption>
				<navigationbaroption name="RUNSEQUENCEHERE" foregroundskinheightpercent="35" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_GRAY3}
						foregroundskinup={getQualifiedClassName(seqListNav_runSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_runSequence_down)}
						foregroundskindisabled={getQualifiedClassName(seqListNav_runSequence_disabled)}>
					RUN FROM HERE
				</navigationbaroption>
				<navigationbaroption blank="true" />
				<navigationbaroption blank="true" />
				<navigationbaroption blank="true" />
			</navigationbar>;
		
		// Number of steps required to load this object
		public static var EDIT_LOAD_STEPS:uint = 1;
		public static var LOAD_STEPS:uint = SequenceBase.BASE_LOAD_STEPS + EDIT_LOAD_STEPS;
	}
}
