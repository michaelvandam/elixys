package Elixys.Views
{
	import Elixys.Assets.Styling;
	import Elixys.Components.Logo;
	import Elixys.Components.Progress;
	import Elixys.Events.*;
	import Elixys.Extended.Form;

	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.TimerEvent;
	import flash.utils.Timer;	

	// This loading view is an extension of our extended Form class
	public class Loading extends Form
	{
		/***
		 * Construction
		 **/
		
		public function Loading(screen:Sprite, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, LOADING, attributes, row, inGroup);
		}
		
		/***
		 * Member functions
		 **/
		
		// Called when this view is first displayed
		public function InitialDisplay():void
		{
			// Get references to the logo and progress
			m_pLogo = Logo(UI.findViewById("Logo"));
			m_pProgress = Progress(UI.findViewById("Progress"));

			// Fade in the logo component
			m_pLogo.Fade(0, 1, 600);

			// Set a timer to delay the fading in of the progress component
			m_pProgressDelayTimer = new Timer(450, 1);
			m_pProgressDelayTimer.addEventListener(TimerEvent.TIMER_COMPLETE, OnProgressDelayTimerComplete);
			m_pProgressDelayTimer.start();
		}

		// Called when the progress delay timer completes
		protected function OnProgressDelayTimerComplete(event:TimerEvent):void
		{
			// Remove the event listener
			m_pProgressDelayTimer.removeEventListener(TimerEvent.TIMER_COMPLETE, OnProgressDelayTimerComplete);
			
			// Fade in the progress component
			m_pProgress.addEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnProgressFadeInComplete);
			m_pProgress.Fade(0, 1, 500);
		}

		// Called when the progress fade in transition is complete
		protected function OnProgressFadeInComplete(event:TransitionCompleteEvent):void
		{
			// Remove the event listener
			m_pProgress.removeEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnProgressFadeInComplete);
			
			// Dispatch a transition complete event
			dispatchEvent(new TransitionCompleteEvent(this));
		}

		// Sets the percent complete
		public function SetProgress(fPercentComplete:Number):void
		{
			m_pProgress.SetProgress(fPercentComplete);	
		}

		// Called when the load is complete
		public function LoadComplete():void
		{
			// Fade out the progress component
			m_pProgress.addEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnProgressFadeOutComplete);
			m_pProgress.Fade(1, 0, 300);
		}
		
		// Called when the progress fade out transition is complete
		protected function OnProgressFadeOutComplete(event:TransitionCompleteEvent):void
		{
			// Remove the event listener
			m_pProgress.removeEventListener(TransitionCompleteEvent.TRANSITIONCOMPLETE, OnProgressFadeOutComplete);

			// Dispatch a transition complete event
			dispatchEvent(new TransitionCompleteEvent(this));
		}

		/***
		 * Member variables
		 **/

		// Loading view XML
		protected static const LOADING:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND}>
				<rows gapV="0" border="false" heights="18%,64%,9%,9%" background={Styling.APPLICATION_BACKGROUND}>
					<frame />
					<columns gapH="0" widths="50%,50%">
						<logo id="Logo" visible="false" />
					</columns>
					<frame />
					<progress id="Progress" />
				</rows>
			</frame>;
		
		// References to components
		private var m_pLogo:Logo;
		private var m_pProgress:Progress;
		
		// Progress delay timer
		protected var m_pProgressDelayTimer:Timer;
	}
}

