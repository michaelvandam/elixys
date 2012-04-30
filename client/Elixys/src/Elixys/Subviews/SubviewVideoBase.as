package Elixys.Subviews
{
	import Elixys.Assets.*;
	import Elixys.Extended.Form;
	import Elixys.Views.SequenceRun;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObjectContainer;
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.geom.Point;
	
	// This subview video base is an extension of the subview unit operation base class
	public class SubviewVideoBase extends SubviewUnitOperationBase
	{
		/***
		 * Construction
		 **/

		public function SubviewVideoBase(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										 sComponentType:String, attributes:Attributes)
		{
			// Call the base constructor
			super(screen, sMode, pElixys, nButtonWidth, sComponentType, RUN_VIDEO, attributes);
			
			// Initialize run mode
			if (m_sMode == Constants.RUN)
			{
				// Get references to the view components
				m_pVideoIconContainer = Form(findViewById("videobase_iconcontainer"));
				m_pVideoLabel = UILabel(findViewById("videobase_label"));
				m_pVideoLabelContainer = Form(findViewById("videobase_labelcontainer"));
				m_pVideoContainer = Form(findViewById("videobase_videocontainer"));
				
				// Add the video icon
				m_pVideoIconSkin = AddSkinAt(videoIcon_mc, 0);
			
				// Find the parent sequence run
				var pParent:DisplayObjectContainer = screen;
				while ((pParent != null) && !(pParent is SequenceRun))
				{
					pParent = pParent.parent;
				}
				if (pParent is SequenceRun)
				{
					m_pSequenceRun = pParent as SequenceRun;
				}
				
				// Initialize the layout
				AdjustPositions();
			}
		}

		/***
		 * Member functions
		 **/

		// Updates the subview
		protected override function Update():void
		{
			// Update run mode
			if (m_sMode == Constants.RUN)
			{
				// Set the video label
				if (m_pComponent)
				{
					m_pVideoLabel.text = "REACTOR " + GetReactor();
				}
			
				// Update the video stream if we're running and visible
				if (m_pRunState.Running && visible)
				{
					m_pSequenceRun.SetVideo(GetReactor(), m_pVideoContainer);
				}
			}
			
			// Call the base implementation
			super.Update();
		}
		
		// Adjusts the view component positions
		protected override function AdjustPositions():void
		{
			// Handle based on our mode
			if (m_sMode == Constants.RUN)
			{
				// Ignore if we haven't finished construction
				if (m_pVideoIconContainer == null)
				{
					return;
				}
				
				// Call the base implementation
				super.AdjustPositions();
				
				// Adjust the video icon position
				var pUpperLeft:Point = globalToLocal(m_pVideoIconContainer.localToGlobal(new Point(0, 0)));
				m_pVideoIconSkin.x = pUpperLeft.x;
				m_pVideoIconSkin.y = pUpperLeft.y + ((m_pVideoIconContainer.attributes.height - m_pVideoIconSkin.height) / 2);
				
				// Adjust the video label position
				m_pVideoLabel.x = 0;
				m_pVideoLabel.y = (m_pVideoLabelContainer.attributes.height - m_pVideoLabel.textHeight) / 2;
			}
			else
			{
				// Call the base implementation
				super.AdjustPositions();
			}
		}
		
		// Returns the reactor number
		protected function GetReactor():uint
		{
			return 0;
		}

		/***
		 * Member variables
		 **/
		
		// Run XML
		protected static const RUN_VIDEO:XML = 
			<frame background={Styling.APPLICATION_BACKGROUND} alignH="fill" alignV="fill">
				<rows id="unitoperationcontainer" heights="3%,6%,5%,75%,11%" gapV="0">
					<frame />
					<columns widths="19,7%,5,93%" gapH="0">
						<frame />
						<frame id="videobase_iconcontainer" />
						<frame />
						<frame id="videobase_labelcontainer">
							<label id="videobase_label" useEmbedded="true">
								<font face="GothamBold" color={Styling.TEXT_BLACK} size="14" />
							</label>
						</frame>
					</columns>
					<frame />
					<columns widths="19%,67%,14%" gapH="0">
						<frame />
						<frame id="videobase_videocontainer" />
					</columns>
					<frame />
				</rows>
			</frame>;
		
		// View components
		protected var m_pVideoIconContainer:Form;
		protected var m_pVideoLabel:UILabel;
		protected var m_pVideoLabelContainer:Form;
		protected var m_pVideoIconSkin:MovieClip;
		protected var m_pVideoContainer:Form;

		// Parent sequence run
		protected var m_pSequenceRun:SequenceRun;
	}
}
