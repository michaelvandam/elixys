package Elixys.Views
{
	import Elixys.Assets.*;
	import Elixys.Events.ButtonEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.State.Sequence;
	import Elixys.JSON.State.State;
	import Elixys.JSON.State.StateSequence;
	import Elixys.JSON.State.Tab;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.utils.*;
	
	// This sequence view screen is an extension of the base sequence class
	public class SequenceView extends SequenceBase
	{
		/***
		 * Construction
		 **/
		
		public function SequenceView(screen:Sprite, pElixys:Elixys, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, pElixys, SEQUENCEVIEW, attributes, row, inGroup);

			// Set our mode
			m_sMode = Constants.VIEW;
		}
		
		/***
		 * Loading functions
		 **/
		
		// Loads the next child component and return true or returns false if the load is complete
		public override function LoadNext():Boolean
		{
			// Load the view children first
			if (m_nChildrenLoaded < VIEW_LOAD_STEPS)
			{
				// Step 1 is loading the navigation bar
				if (m_nChildrenLoaded == 0)
				{
					LoadNavigationBar("sequenceview_navigationbar_container", NAVIGATION);
				}

				// Step 2 is loading the tab bar
				if (m_nChildrenLoaded == 1)
				{
					var pTabs:Array = new Array();
					pTabs.push(Tab.CreateTab("CASSETTES", "CASSETTES"));
					LoadTabBar("sequenceview_tabbar_container", pTabs, "CASSETTES");
				}

				// Step 3 is loading the cassettes component
				if (m_nChildrenLoaded == 2)
				{
					LoadSequenceCassettes("sequenceview_cassettes_container");
				}

				// Step 4 is loading the sequencer
				if (m_nChildrenLoaded == 3)
				{
					LoadSequencer("sequenceview_sequencer_container", SEQUENCER);
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
		
		// Updates the sequence
		public override function UpdateSequence(pSequence:Sequence):void
		{
			// Call the base handler
			super.UpdateSequence(pSequence);
		}
		
		/***
		 * Member variables
		 **/

		// Sequence view XML
		protected static const SEQUENCEVIEW:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND} alignH="fill" alignV="fill">
				<rows gapV="0" border="false" heights="18%,61%,21%" alignH="fill" alignV="fill">
					<frame id="sequenceview_navigationbar_container" alignV="fill" alignH="fill" />
					<rows heights="8%,3%,89%" gapV="0" alignV="fill" alignH="fill">
						<frame id="sequence_title_container" />
						<frame />
						<columns widths="20,34%,4,66%" gapH="0" alignV="fill" alignH="fill">
							<frame />
							<rows heights="10%,90%" gapV="0" alignV="fill" alignH="fill">
								<frame id="sequenceview_tabbar_container" />
								<frame id="sequenceview_cassettes_container" />
							</rows>
							<rows heights="9%,85%,6%" gapV="0" alignV="fill" alignH="fill">
								<frame />
								<frame background={Styling.TABBAR_LINE} />
							</rows>
							<frame id="unitoperation_container" />
						</columns>
					</rows>
					<frame id="sequenceview_sequencer_container" alignV="fill" alignH="fill" />
				</rows>
			</frame>;
		
		// Navigation bar XML
		protected static const NAVIGATION:XML =
			<navigationbar alignH="fill" alignV="fill" skin={getQualifiedClassName(blueNavigationBar_mc)} rightpadding="20">
				<navigationbaroption name="SEQUENCER" backgroundskinheightpercent="72" foregroundskinheightpercent="30"
						fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_GRAY1} disabledTextColor={Styling.TEXT_GRAY1}
						backgroundskinup={getQualifiedClassName(mainNav_activeBtnOutline_up)}
						backgroundskindown={getQualifiedClassName(mainNav_activeBtnOutline_down)}
						backgroundskindisabled={getQualifiedClassName(mainNav_activeBtnOutline_up)}
						foregroundskinup={getQualifiedClassName(mainNav_sequencer_active)}
						foregroundskindown={getQualifiedClassName(mainNav_sequencer_down)} 
						foregroundskindisabled={getQualifiedClassName(mainNav_sequencer_disabled)}>
					SEQUENCER
				</navigationbaroption>
				<navigationbaroption name="EDITSEQUENCE" foregroundskinheightpercent="30" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_BLUE3}
						foregroundskinup={getQualifiedClassName(seqListNav_editSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_editSequence_down)} 
						foregroundskindisabled={getQualifiedClassName(seqListNav_editSequence_disabled)}>
					EDIT SEQUENCE
				</navigationbaroption>
				<navigationbaroption name="RUNSEQUENCE" foregroundskinheightpercent="30" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_BLUE3}
						foregroundskinup={getQualifiedClassName(seqListNav_runSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_runSequence_down)}
						foregroundskindisabled={getQualifiedClassName(seqListNav_runSequence_disabled)}>
					RUN SEQUENCE
				</navigationbaroption>
				<navigationbaroption name="RUNSEQUENCEHERE" foregroundskinheightpercent="30" fontSize="12" fontFace="GothamMedium"
						enabledTextColor={Styling.TEXT_WHITE} disabledTextColor={Styling.TEXT_BLUE3}
						foregroundskinup={getQualifiedClassName(seqListNav_runSequence_up)}
						foregroundskindown={getQualifiedClassName(seqListNav_runSequence_down)}
						foregroundskindisabled={getQualifiedClassName(seqListNav_runSequence_disabled)}>
					RUN FROM HERE
				</navigationbaroption>
				<navigationbaroption blank="true" />
				<navigationbaroption blank="true" />
				<navigationbaroption blank="true" />
			</navigationbar>;

		// Sequencer XML
		protected static const SEQUENCER:XML =
			<sequencer mode={Constants.VIEW} alignH="fill" alignV="fill"/>;
		
		// Number of steps required to load this object
		public static var VIEW_LOAD_STEPS:uint = 4;
		public static var LOAD_STEPS:uint = SequenceBase.BASE_LOAD_STEPS + VIEW_LOAD_STEPS;
	}
}
